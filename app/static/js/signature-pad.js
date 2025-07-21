// Signature pad functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get the canvas element
    const canvas = document.getElementById('signature-pad');
    if (!canvas) return;

    // Initialize the SignaturePad
    const signaturePad = new SignaturePad(canvas, {
        backgroundColor: 'rgb(255, 255, 255)',
        penColor: 'rgb(0, 0, 0)'
    });

    // Clear signature button
    document.getElementById('clear-signature').addEventListener('click', function() {
        signaturePad.clear();
    });

    // Color picker
    const colorPicker = document.getElementById('signature-color');
    if (colorPicker) {
        colorPicker.addEventListener('change', function() {
            signaturePad.penColor = this.value;
        });
    }

    // Pen width
    const penWidth = document.getElementById('pen-width');
    if (penWidth) {
        penWidth.addEventListener('change', function() {
            signaturePad.minWidth = 0.5;
            signaturePad.maxWidth = this.value;
        });
    }

    // Save signature
    document.getElementById('save-signature').addEventListener('click', function() {
        if (signaturePad.isEmpty()) {
            alert('Please provide a signature first.');
            return;
        }

        const dataURL = signaturePad.toDataURL('image/png');

        // Create a blob
        const blob = dataURLtoBlob(dataURL);
        const formData = new FormData();
        formData.append('signature', blob, 'signature.png');

        // Send to server
        fetch('/api/signatures/save', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Signature saved successfully!');
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            alert('Error saving signature: ' + error);
        });
    });

    // Convert data URL to Blob
    function dataURLtoBlob(dataURL) {
        const parts = dataURL.split(';base64,');
        const contentType = parts[0].split(':')[1];
        const raw = window.atob(parts[1]);
        const rawLength = raw.length;
        const uInt8Array = new Uint8Array(rawLength);

        for (let i = 0; i < rawLength; ++i) {
            uInt8Array[i] = raw.charCodeAt(i);
        }

        return new Blob([uInt8Array], { type: contentType });
    }
});