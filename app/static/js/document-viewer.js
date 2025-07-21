// Document viewer functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the PDF viewer
    const pdfContainer = document.getElementById('pdf-container');
    const pdfUrl = pdfContainer.dataset.url;
    let currentPage = 1;
    let totalPages = 0;

    // PDF.js loading
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://mozilla.github.io/pdf.js/build/pdf.worker.js';

    // Load the PDF
    pdfjsLib.getDocument(pdfUrl).promise.then(function(pdf) {
        totalPages = pdf.numPages;
        document.getElementById('total-pages').textContent = totalPages;

        // Initial render
        renderPage(pdf, currentPage);

        // Previous page button
        document.getElementById('prev-page').addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                renderPage(pdf, currentPage);
                document.getElementById('current-page').textContent = currentPage;
            }
        });

        // Next page button
        document.getElementById('next-page').addEventListener('click', function() {
            if (currentPage < totalPages) {
                currentPage++;
                renderPage(pdf, currentPage);
                document.getElementById('current-page').textContent = currentPage;
            }
        });

        // Zoom controls
        let scale = 1.0;
        document.getElementById('zoom-in').addEventListener('click', function() {
            scale += 0.25;
            renderPage(pdf, currentPage);
        });

        document.getElementById('zoom-out').addEventListener('click', function() {
            if (scale > 0.5) {
                scale -= 0.25;
                renderPage(pdf, currentPage);
            }
        });
    });

    function renderPage(pdf, pageNumber) {
        pdf.getPage(pageNumber).then(function(page) {
            const viewport = page.getViewport({ scale: scale });

            // Prepare canvas for rendering
            const canvas = document.getElementById('pdf-canvas');
            const context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            // Render PDF page into canvas context
            const renderContext = {
                canvasContext: context,
                viewport: viewport
            };

            page.render(renderContext);
        });
    }
});