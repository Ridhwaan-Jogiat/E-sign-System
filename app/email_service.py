# app/email.py
from flask import current_app, url_for
from flask_mail import Message
from app import mail


def send_email(subject, recipient, body):
    """Send a simple email"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body,
            sender=current_app.config['MAIL_USERNAME']
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send email: {str(e)}')
        return False


def send_document_notification(recipient_email, doc_data):
    """Notify boss when a document needs signature"""
    subject = "New Document Awaiting Signature"
    # Generate document link
    with current_app.app_context():
        doc_link = url_for('documents.view_document', document_id=doc_data['id'], _external=True)
    body = f"""
Hello,

You have a new document awaiting your signature:

Document: {doc_data['original_filename']}
Client: {doc_data.get('client', '-')}
Work: {doc_data.get('work', '-')}
Type of Document: {doc_data.get('document_type', '-')}
Comment: {doc_data.get('comment', '-')}

View Document: {doc_link}

Please log in to the E-Signature System to review and sign the document.

Best regards,
E-Signature System
"""
    return send_email(subject, recipient_email, body)


def send_signature_completion_notification(recipient_email, document_name, document_id):
    """Notify employee when document is signed"""
    subject = "Document Signed Successfully"
    with current_app.app_context():
        doc_link = url_for('documents.view_document', document_id=document_id, _external=True)
    body = f"""
Hello,

Your document has been signed!

Document: {document_name}

You can now download or view the signed document here:
{doc_link}

Best regards,
E-Signature System
"""
    return send_email(subject, recipient_email, body)