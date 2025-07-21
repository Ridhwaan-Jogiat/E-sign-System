import os
import uuid
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory, \
    send_file, jsonify
from datetime import datetime
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db
from app.models import Document, User
from app.email_service import send_document_notification, send_email
from app.add_employee import add_employee
import threading

documents_bp = Blueprint('documents', __name__)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_DOCUMENT_EXTENSIONS']


def async_send_document_notification(email, doc_data):
    app = current_app._get_current_object()
    def send_with_context():
        with app.app_context():
            send_document_notification(email, doc_data)
    threading.Thread(target=send_with_context).start()


@documents_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_boss():
        # Boss sees pending documents from all users
        pending_documents = Document.query.filter_by(status='pending').all()
        signed_documents = Document.query.filter_by(status='signed', signed_by=current_user.id).all()
        return render_template('boss/dashboard.html',
                               pending_documents=pending_documents,
                               signed_documents=signed_documents)
    else:
        # Employees see their own documents
        pending_documents = Document.query.filter_by(uploaded_by=current_user.id, status='pending').all()
        signed_documents = Document.query.filter_by(uploaded_by=current_user.id, status='signed').all()
        return render_template('employee/dashboard.html', 
                             pending_documents=pending_documents,
                             signed_documents=signed_documents)


@documents_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_document():
    # Employee upload
    if current_user.is_boss():
        flash('Only employees can upload documents here')
        return redirect(url_for('documents.dashboard'))

    if request.method == 'POST':
        file = request.files.get('document')
        if not file or file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            save_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, filename)
            file.save(file_path)
            # Get extra details from form
            client = request.form.get('client')
            work = request.form.get('work')
            document_type = request.form.get('document_type')
            comment = request.form.get('comment')
            new_doc = Document(
                filename=filename,
                original_filename=original_filename,
                file_path=file_path,
                file_type=ext,
                uploaded_by=current_user.id,
                status='pending',
                client=client,
                work=work,
                document_type=document_type,
                comment=comment
            )
            db.session.add(new_doc)
            db.session.commit()
            # Send notification to boss asynchronously
            boss = User.query.filter_by(role='boss').first()
            if boss:
                try:
                    doc_data = {
                        'id': new_doc.id,
                        'original_filename': new_doc.original_filename,
                        'client': new_doc.client,
                        'work': new_doc.work,
                        'document_type': new_doc.document_type,
                        'comment': new_doc.comment
                    }
                    async_send_document_notification(boss.email, doc_data)
                except Exception as e:
                    current_app.logger.error(f'Failed to send notification: {str(e)}')
            flash('Document uploaded successfully')
            return redirect(url_for('documents.dashboard'))
    return render_template('employee/document_upload.html')


@documents_bp.route('/upload_for_sign', methods=['POST'])
@login_required
def upload_for_sign():
    # Boss uploads a document to sign
    if not current_user.is_boss():
        flash('Only boss can upload documents for signing')
        return redirect(url_for('documents.dashboard'))

    file = request.files.get('document')
    if not file or file.filename == '':
        flash('No selected file')
        return redirect(url_for('documents.dashboard'))
    if allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        ext = original_filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        save_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        file.save(file_path)
        new_doc = Document(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_type=ext,
            uploaded_by=current_user.id,
            status='pending'
        )
        db.session.add(new_doc)
        db.session.commit()
        flash('Document uploaded for your signature')
    else:
        flash('File type not allowed')
    return redirect(url_for('documents.dashboard'))


@documents_bp.route('/document/<int:document_id>')
@login_required
def view_document(document_id):
    document = Document.query.get_or_404(document_id)
    if not current_user.is_boss() and document.uploaded_by != current_user.id:
        flash('You do not have permission to view this document')
        return redirect(url_for('documents.dashboard'))
    file_path = document.signed_file_path if document.status == 'signed' else document.file_path
    filename = os.path.basename(file_path)
    return render_template('shared/document_viewer.html', document=document, display_filename=filename)


@documents_bp.route('/download/<int:document_id>')
@login_required
def download_document(document_id):
    document = Document.query.get_or_404(document_id)
    if not current_user.is_boss() and document.uploaded_by != current_user.id:
        flash('You do not have permission to download this document')
        return redirect(url_for('documents.dashboard'))
    file_path = document.signed_file_path if document.status == 'signed' else document.file_path
    return send_file(file_path, as_attachment=True, download_name=document.original_filename)


@documents_bp.route('/view-signed/<int:document_id>')
@login_required
def view_signed(document_id):
    doc = Document.query.get_or_404(document_id)
    if not current_user.is_boss() and doc.uploaded_by != current_user.id:
        flash('You do not have permission to view this document')
        return redirect(url_for('documents.dashboard'))
    if not doc.signed_file_path or not os.path.exists(doc.signed_file_path):
        flash('Signed file not found')
        return redirect(url_for('documents.dashboard'))
    return send_file(doc.signed_file_path, mimetype='application/pdf', as_attachment=False)


@documents_bp.route('/save-signature-positions/<int:document_id>', methods=['POST'])
@login_required
def save_signature_positions(document_id):
    document = Document.query.get_or_404(document_id)

    # Only the employee who uploaded the document can place signatures
    if document.uploaded_by != current_user.id:
        return jsonify({'success': False, 'message': 'You do not have permission to modify this document'}), 403

    if document.status != 'pending':
        return jsonify({'success': False, 'message': 'Document is not pending'}), 400

    data = request.get_json()
    if not data or 'positions' not in data:
        return jsonify({'success': False, 'message': 'Invalid position data'}), 400

    try:
        # Validate positions data
        for pos in data['positions']:
            if 'type' not in pos:
                pos['type'] = 'signature'  # Default to signature if type not specified
            if 'page' not in pos or 'x' not in pos or 'y' not in pos:
                return jsonify({'success': False, 'message': 'Invalid position format'}), 400

        # Store JSON string of positions in the database
        document.signature_placement = json.dumps(data['positions'])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Signature positions saved'})
    except Exception as e:
        current_app.logger.error(f"Error saving signature positions: {str(e)}")
        return jsonify({'success': False, 'message': f'Error saving positions: {str(e)}'}), 500



@documents_bp.route('/get-signature-positions/<int:document_id>')
@login_required
def get_signature_positions(document_id):
    document = Document.query.get_or_404(document_id)

    if not current_user.is_boss() and document.uploaded_by != current_user.id:
        return jsonify({'success': False, 'message': 'You do not have permission to view this document'}), 403

    if not document.signature_placement:
        return jsonify({'success': True, 'positions': []})

    try:
        positions = json.loads(document.signature_placement)
        # Ensure each position has a type field
        for pos in positions:
            if 'type' not in pos:
                pos['type'] = 'signature'  # Default to signature if type not specified
        return jsonify({'success': True, 'positions': positions})
    except Exception as e:
        current_app.logger.error(f"Error parsing signature positions: {str(e)}")
        return jsonify({'success': False, 'message': f'Error parsing positions: {str(e)}'}), 500


@documents_bp.route('/delete-document/<int:document_id>', methods=['POST'])
@login_required
def delete_document(document_id):
    document = Document.query.get_or_404(document_id)
    
    # Check if user has permission to delete
    if not current_user.is_boss() and document.uploaded_by != current_user.id:
        return jsonify({'success': False, 'message': 'You do not have permission to delete this document'}), 403

    try:
        # Delete the document files
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
        if document.signed_file_path and os.path.exists(document.signed_file_path):
            os.remove(document.signed_file_path)

        # Delete from database
        db.session.delete(document)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Document deleted successfully'})
    except Exception as e:
        current_app.logger.error(f'Error deleting document: {str(e)}')
        return jsonify({'success': False, 'message': f'Error deleting document: {str(e)}'}), 500