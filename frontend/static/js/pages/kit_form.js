const FILE_ACCEPT = '.png,.jpg,.jpeg,.mp3,.aia,.aix,.pdf';

const createAssetRow = (sectionIndex, assetIndex, existingUrl = '', existingLabel = '') => {
    const row = document.createElement('div');
    row.className = 'row g-3 align-items-end mb-3 asset-row';
    row.dataset.assetIndex = assetIndex;

    row.innerHTML = `
        <div class="col-lg-5">
            <label class="form-label">Asset File</label>
            <input type="file" name="section_${sectionIndex}_file_${assetIndex}" class="form-control" accept="${FILE_ACCEPT}">
            ${existingUrl ? `<input type="hidden" name="section_${sectionIndex}_existing_url_${assetIndex}" value="${existingUrl}">` : ''}
            ${existingUrl ? `<small class="text-muted d-block mt-1">Existing: <a href="${existingUrl}" target="_blank">View file</a></small>` : ''}
        </div>
        <div class="col-lg-5">
            <label class="form-label">File Label</label>
            <input type="text" name="section_${sectionIndex}_label_${assetIndex}" class="form-control" value="${existingLabel}">
        </div>
        <div class="col-lg-2">
            <button type="button" class="btn btn-outline-danger w-100 remove-asset">Remove</button>
        </div>
    `;

    return row;
};

const createSection = (sectionIndex) => {
    const section = document.createElement('div');
    section.className = 'border rounded-3 p-3 mb-4 kit-section';
    section.dataset.sectionIndex = sectionIndex;

    section.innerHTML = `
        <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
            <div class="flex-grow-1 me-2">
                <label class="form-label">Section Name</label>
                <input type="text" name="section_${sectionIndex}_name" class="form-control" required>
            </div>
            <button type="button" class="btn btn-outline-danger mt-4 remove-section">Remove Section</button>
        </div>
        <input type="hidden" name="section_${sectionIndex}_asset_count" class="asset-count" value="0">
        <div class="asset-rows"></div>
        <button type="button" class="btn btn-outline-secondary add-asset">Add Asset</button>
    `;

    return section;
};

const updateSectionCount = () => {
    const sectionsContainer = document.getElementById('sectionsContainer');
    const sectionCountInput = document.getElementById('sectionCount');
    if (sectionsContainer && sectionCountInput) {
        const sections = sectionsContainer.querySelectorAll('.kit-section');
        sectionCountInput.value = sections.length;
    }
};

const updateAssetCount = (section) => {
    const assetCountInput = section.querySelector('.asset-count');
    const assets = section.querySelectorAll('.asset-row');
    if (assetCountInput) {
        assetCountInput.value = assets.length;
    }
};

const attachSectionHandlers = (section) => {
    const addAssetButton = section.querySelector('.add-asset');
    const assetRows = section.querySelector('.asset-rows');

    if (addAssetButton && assetRows) {
        addAssetButton.addEventListener('click', () => {
            const sectionIndex = section.dataset.sectionIndex;
            const assetIndex = assetRows.querySelectorAll('.asset-row').length;
            const row = createAssetRow(sectionIndex, assetIndex);
            assetRows.appendChild(row);
            updateAssetCount(section);
        });
    }

    section.addEventListener('click', (event) => {
        if (event.target.classList.contains('remove-asset')) {
            const row = event.target.closest('.asset-row');
            if (row) {
                row.remove();
                updateAssetCount(section);
            }
        }
        if (event.target.classList.contains('remove-section')) {
            section.remove();
            updateSectionCount();
        }
    });
};

const initKitForm = () => {
    const form = document.getElementById('kitForm');
    const sectionsContainer = document.getElementById('sectionsContainer');
    const addSectionBtn = document.getElementById('addSectionBtn');

    if (!form || !sectionsContainer || !addSectionBtn) {
        return;
    }

    sectionsContainer.querySelectorAll('.kit-section').forEach((section) => {
        attachSectionHandlers(section);
        updateAssetCount(section);
    });

    addSectionBtn.addEventListener('click', () => {
        const sectionIndex = sectionsContainer.querySelectorAll('.kit-section').length;
        const section = createSection(sectionIndex);
        sectionsContainer.appendChild(section);
        attachSectionHandlers(section);
        updateSectionCount();
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        updateSectionCount();
        sectionsContainer.querySelectorAll('.kit-section').forEach(updateAssetCount);

        const kitId = form.dataset.kitId;
        const endpoint = kitId ? `/api/admin/kits/${kitId}` : '/api/admin/kits';
        const method = kitId ? 'PUT' : 'POST';
        const formData = new FormData(form);

        try {
            const response = await fetch(endpoint, {
                method,
                body: formData,
            });

            if (response.ok) {
                window.location.href = '/admin/manage-kits';
            } else {
                const error = await response.json().catch(() => null);
                alert(error?.detail || 'Failed to save kit.');
            }
        } catch (error) {
            console.error('Error saving kit:', error);
            alert('An error occurred while saving.');
        }
    });
};

document.addEventListener('DOMContentLoaded', initKitForm);
