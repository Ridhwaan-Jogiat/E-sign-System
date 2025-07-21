import os
import uuid
import json
from datetime import datetime
from app.email_service import send_signature_completion_notification
import threading

import pytz
from PIL import Image
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Document, Signature, User

signatures_bp = Blueprint('signatures', __name__)


@signatures_bp.route('/manage-signature', methods=['GET', 'POST'])
@login_required
def manage_signature():
    if not current_user.is_boss():
        flash('Only the boss can manage signatures')
        return redirect(url_for('documents.dashboard'))

    signatures = Signature.query.filter_by(user_id=current_user.id).order_by(Signature.created_date.desc()).all()

    if request.method == 'POST':
        if 'signature' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['signature']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        try:
            signature_type = request.form.get('signature_type', 'signature')
            display_name = request.form.get('display_name', '')
            # Only allow one active signature per type (signature, initial, company)
            if signature_type in ['signature', 'company']:
                # Deactivate all other signatures of this type for this user
                Signature.query.filter_by(user_id=current_user.id, signature_type=signature_type).update({'is_active': False})
                db.session.commit()

            upload_dir = os.path.join(current_app.static_folder, 'uploads', 'signatures')
            os.makedirs(upload_dir, exist_ok=True)

            filename = f"{uuid.uuid4().hex}.png"
            full_path = os.path.join(upload_dir, filename)
            img = Image.open(file).convert('RGBA')
            datas = img.getdata()
            newData = []
            for item in datas:
                # If pixel is almost white, make it transparent
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)
            img.putdata(newData)
            bbox = img.getbbox()
            if bbox:
                img = img.crop(bbox)
            img.save(full_path)

            relative_path = f"uploads/signatures/{filename}"
            new_signature = Signature(
                user_id=current_user.id,
                signature_path=relative_path,
                is_active=False,
                signature_type=signature_type,
                display_name=display_name
            )
            db.session.add(new_signature)
            db.session.commit()

            flash('Signature uploaded successfully')
            return redirect(url_for('signatures.manage_signature'))
        except Exception as e:
            current_app.logger.error(f'Error processing signature: {str(e)}')
            flash(f'Error processing signature: {str(e)}')
            return redirect(request.url)

    return render_template('boss/signature_manager.html', signatures=signatures)


@signatures_bp.route('/set-active-signature/<string:sig_id>', methods=['POST'])
@login_required
def set_active_signature(sig_id):
    if not current_user.is_boss():
        return jsonify({'success': False, 'message': 'Only the boss can manage signatures'}), 403

    try:
        sig_id_int = int(sig_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid signature ID'}), 400

    signature = Signature.query.filter_by(id=sig_id_int, user_id=current_user.id).first()
    if not signature:
        return jsonify({'success': False, 'message': 'Signature not found'}), 404

    Signature.query.filter_by(user_id=current_user.id, signature_type=signature.signature_type).update(
        {'is_active': False})

    signature.is_active = True
    db.session.commit()

    return jsonify({'success': True, 'message': 'Signature activated'})


@signatures_bp.route('/get_active_signature/<string:sig_type>', methods=['GET'])
@login_required
def get_active_signature(sig_type='signature'):
    signature = None
    if current_user.is_boss():
        signature = Signature.query.filter_by(user_id=current_user.id, is_active=True, signature_type=sig_type).first()
    else:
        boss = User.query.filter_by(role='boss').first()
        if boss:
            signature = Signature.query.filter_by(user_id=boss.id, is_active=True, signature_type=sig_type).first()

    if not signature:
        return jsonify({'success': False, 'message': f'No active {sig_type} found'}), 404

    sig_url = url_for('static', filename=signature.signature_path)
    return jsonify({
        'success': True,
        'signature': {
            'id': signature.id,
            'path': sig_url,
            'type': signature.signature_type,
            'display_name': signature.display_name,
            'created_date': signature.created_date.strftime('%Y-%m-%d %H:%M')
        }
    })


@signatures_bp.route('/sign-document/<int:document_id>', methods=['POST'])
@login_required
def sign_document(document_id):
    if not current_user.is_boss():
        return jsonify({'success': False, 'message': 'Only the boss can sign documents'}), 403

    document = Document.query.get_or_404(document_id)
    if document.status != 'pending':
        return jsonify({'success': False, 'message': 'Document is not pending signature'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request data'}), 400

    signing_method = data.get('signing_method', 'manual')
    document.signing_method = signing_method

    positions = []

    if signing_method == 'auto' and document.signature_placement:
        try:
            positions = json.loads(document.signature_placement)
            # Get the signature IDs from the request
            signature_id = data.get('signatureId')  # boss personal
            initial_id = data.get('initialId')      # initials
            company_id = data.get('companyId')      # company signature

            if not signature_id or not initial_id or not company_id:
                return jsonify({'success': False, 'message': 'Missing signature, initial, or company ID for auto-signing'}), 400

            # Ensure each position has a signatureId from the request
            for pos in positions:
                if 'type' not in pos:
                    pos['type'] = 'signature'  # Default to signature if type not specified
                # Get the appropriate signature ID based on type
                if pos['type'] == 'initial':
                    pos['signatureId'] = initial_id
                elif pos['type'] == 'company':
                    pos['signatureId'] = company_id
                else:
                    pos['signatureId'] = signature_id

            current_app.logger.info(f"Auto-signing with {len(positions)} positions")
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error parsing employee signature positions: {str(e)}'}), 500
    else:
        if 'positions' not in data or not data['positions']:
            return jsonify({'success': False, 'message': 'No signature positions provided'}), 400
        positions = data['positions']

    try:
        current_app.logger.info(f"Signing document {document_id} with method {signing_method}")
        current_app.logger.info(f"Number of positions: {len(positions)}")
        for i, pos in enumerate(positions):
            current_app.logger.info(
                f"Position {i}: page={pos.get('page')}, type={pos.get('type')}, signatureId={pos.get('signatureId')}")

        signed_file_path = apply_signature_to_pdf(document.file_path, current_user.signatures, positions)
        document.status = 'signed'
        document.signed_file_path = signed_file_path
        document.signed_date = datetime.now(pytz.utc)
        document.signed_by = current_user.id
        db.session.commit()

        current_app.logger.info(f"Document signed successfully: {signed_file_path}")

        if document.uploader:
            try:
                async_send_signature_completion_notification(
                    document.uploader.email,
                    document.original_filename,
                    document.id
                )
            except Exception as e:
                current_app.logger.error(f'Failed to send completion notification: {str(e)}')

        return jsonify({'success': True, 'message': 'Document signed successfully'})
    except Exception as e:
        current_app.logger.error(f"Error signing document: {str(e)}")
        return jsonify({'success': False, 'message': f'Error signing document: {str(e)}'}), 500


def apply_signature_to_pdf(pdf_path, boss_signatures, positions):
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from io import BytesIO
    from PIL import Image as PILImage

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Create a mapping of signature IDs to their paths
    signature_paths = {}
    signature_aspects = {}  # Store aspect ratios
    for sig in boss_signatures:
        sig_path = os.path.join(current_app.static_folder, sig.signature_path)
        signature_paths[str(sig.id)] = sig_path

        # Get the actual image dimensions for aspect ratio
        try:
            with PILImage.open(sig_path) as img:
                width, height = img.size
                signature_aspects[str(sig.id)] = width / height if height > 0 else 1
        except:
            signature_aspects[str(sig.id)] = 3  # Default aspect ratio (150/50)

    # Group positions by page
    positions_by_page = {}
    for pos in positions:
        page = int(pos['page'])
        sig_id = pos.get('signatureId')

        if not sig_id or str(sig_id) not in signature_paths:
            continue  # Skip if no valid signature ID

        pos['sig_path'] = signature_paths[str(sig_id)]
        pos['aspect_ratio'] = signature_aspects.get(str(sig_id), 3)
        positions_by_page.setdefault(page, []).append(pos)

    for page_num, page in enumerate(reader.pages):
        w_pt = float(page.mediabox.width)
        h_pt = float(page.mediabox.height)

        if page_num in positions_by_page:
            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=(w_pt, h_pt))

            for pos in positions_by_page[page_num]:
                sig_path = pos.get('sig_path')
                if not sig_path:
                    continue

                sx, sy = float(pos['x']), float(pos['y'])
                sw, sh = float(pos.get('width', 150)), float(pos.get('height', 50))
                aspect_ratio = pos.get('aspect_ratio', 3)
                sig_type = pos.get('type', 'signature')

                # Apply maximum dimensions for initials to prevent them from being too large
                if sig_type == 'initial':
                    sw = min(sw, 80)  # Max width for initials
                    sh = min(sh, 35)  # Max height for initials
                elif sig_type == 'company':
                    sw = min(sw, 200)  # Company signature can be larger
                    sh = min(sh, 60)

                # For initials, use the actual image size (don't stretch to fill box)
                if sig_type == 'initial':
                    # Get actual image dimensions
                    try:
                        with PILImage.open(sig_path) as img:
                            img_width, img_height = img.size
                            # Scale down if image is larger than box, but never scale up
                            scale_factor = min(sw / img_width, sh / img_height, 1.0)
                            actual_width = img_width * scale_factor
                            actual_height = img_height * scale_factor
                    except:
                        # Fallback to box dimensions if can't read image
                        actual_width = sw
                        actual_height = sh
                else:
                    # For full signatures, fit to box while maintaining aspect ratio
                    box_aspect = sw / sh if sh > 0 else 1

                    if aspect_ratio > box_aspect:
                        # Signature is wider than box - fit to width
                        actual_width = sw
                        actual_height = sw / aspect_ratio
                    else:
                        # Signature is taller than box - fit to height
                        actual_height = sh
                        actual_width = sh * aspect_ratio

                # Center the signature within the box
                x_offset = (sw - actual_width) / 2
                y_offset = (sh - actual_height) / 2

                corrected_y = h_pt - sy - sh + y_offset
                c.drawImage(sig_path, sx + x_offset, corrected_y,
                            width=actual_width, height=actual_height,
                            mask='auto', preserveAspectRatio=True)

            c.save()
            packet.seek(0)
            overlay = PdfReader(packet).pages[0]
            page.merge_page(overlay)

        writer.add_page(page)

    signed_filename = f"signed_{uuid.uuid4().hex}.pdf"
    out_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
    os.makedirs(out_dir, exist_ok=True)
    signed_path = os.path.join(out_dir, signed_filename)

    with open(signed_path, 'wb') as out_f:
        writer.write(out_f)

    return signed_path


@signatures_bp.route('/get_all_signatures', methods=['GET'])
@login_required
def get_all_signatures():
    if current_user.is_boss():
        signatures = Signature.query.filter_by(user_id=current_user.id).all()
    else:
        boss = User.query.filter_by(role='boss').first()
        signatures = Signature.query.filter_by(user_id=boss.id).all() if boss else []

    signatures_data = []
    for sig in signatures:
        signatures_data.append({
            'id': sig.id,
            'path': url_for('static', filename=sig.signature_path),
            'type': sig.signature_type,
            'display_name': sig.display_name,
            'created_date': sig.created_date.strftime('%Y-%m-%d %H:%M'),
            'is_default': sig.is_default
        })

    return jsonify({
        'success': True,
        'signatures': signatures_data
    })


@signatures_bp.route('/delete-signature/<int:signature_id>', methods=['POST'])
@login_required
def delete_signature(signature_id):
    if not current_user.is_boss():
        return jsonify({'success': False, 'message': 'Only the boss can delete signatures'}), 403

    signature = Signature.query.get_or_404(signature_id)

    # Check if signature belongs to the current user
    if signature.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'You can only delete your own signatures'}), 403

    try:
        # Delete the signature file
        if signature.signature_path:
            file_path = os.path.join(current_app.static_folder, signature.signature_path)
            if os.path.exists(file_path):
                os.remove(file_path)

        # Delete from database
        db.session.delete(signature)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Signature deleted successfully'})
    except Exception as e:
        current_app.logger.error(f'Error deleting signature: {str(e)}')
        return jsonify({'success': False, 'message': f'Error deleting signature: {str(e)}'}), 500


def async_send_signature_completion_notification(email, filename, document_id):
    app = current_app._get_current_object()
    def send_with_context():
        with app.app_context():
            send_signature_completion_notification(email, filename, document_id)
    threading.Thread(target=send_with_context).start()


@signatures_bp.route('/set-default-signature/<int:sig_id>', methods=['POST'])
@login_required
def set_default_signature(sig_id):
    if not current_user.is_boss():
        return jsonify({'success': False, 'message': 'Only the boss can set default signatures'}), 403

    signature = Signature.query.filter_by(id=sig_id, user_id=current_user.id).first()
    if not signature:
        return jsonify({'success': False, 'message': 'Signature not found'}), 404

    # Unset other defaults of the same type for this user
    Signature.query.filter_by(user_id=current_user.id, signature_type=signature.signature_type).update({'is_default': False})
    signature.is_default = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Default signature set'})


@signatures_bp.route('/unset-default-signature/<int:sig_id>', methods=['POST'])
@login_required
def unset_default_signature(sig_id):
    if not current_user.is_boss():
        return jsonify({'success': False, 'message': 'Only the boss can unset default signatures'}), 403

    signature = Signature.query.filter_by(id=sig_id, user_id=current_user.id).first()
    if not signature:
        return jsonify({'success': False, 'message': 'Signature not found'}), 404

    signature.is_default = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Default signature unset'})