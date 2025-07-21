// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltips.length > 0) {
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    }

    // Document filtering
    const filterInput = document.getElementById('filter-documents');
    if (filterInput) {
        filterInput.addEventListener('keyup', function() {
            const filterValue = this.value.toLowerCase();
            const documentRows = document.querySelectorAll('.document-table tbody tr');

            documentRows.forEach(row => {
                const documentName = row.querySelector('td:first-child').textContent.toLowerCase();
                const uploadedBy = row.querySelector('td:nth-child(2)').textContent.toLowerCase();

                if (documentName.includes(filterValue) || uploadedBy.includes(filterValue)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Refresh document list periodically
    let refreshInterval;
    const refreshToggle = document.getElementById('auto-refresh');

    if (refreshToggle) {
        refreshToggle.addEventListener('change', function() {
            if (this.checked) {
                refreshInterval = setInterval(refreshDocumentList, 30000); // Refresh every 30 seconds
            } else {
                clearInterval(refreshInterval);
            }
        });
    }

    function refreshDocumentList() {
        const documentList = document.querySelector('.document-table tbody');
        const currentPage = window.location.pathname;

        fetch(`${currentPage}?ajax=true`)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newDocumentList = doc.querySelector('.document-table tbody');

                if (newDocumentList) {
                    documentList.innerHTML = newDocumentList.innerHTML;
                }
            })
            .catch(error => console.error('Error refreshing document list:', error));
    }
});