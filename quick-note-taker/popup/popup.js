const noteInput = document.getElementById('noteInput');
const categorySelect = document.getElementById('categorySelect');
const colorPicker = document.getElementById('colorPicker');
const saveNoteButton = document.getElementById('saveNote');
const notesList = document.getElementById('notesList');

let notes = [];

// Load notes from storage
function loadNotes() {
    chrome.storage.local.get(['notes'], (result) => {
        if (result.notes) {
            notes = result.notes;
            renderNotes();
        }
    });
}

// Render notes
function renderNotes() {
    notesList.innerHTML = '';
    notes.forEach((note, index) => {
        const noteDiv = document.createElement('div');
        noteDiv.style.backgroundColor = note.color;
        noteDiv.className = 'note';
        noteDiv.innerHTML = `<strong>${note.category}</strong>: ${note.text}`;
        notesList.appendChild(noteDiv);
    });
}

// Save note
saveNoteButton.addEventListener('click', () => {
    const noteText = noteInput.value;
    const category = categorySelect.value;
    const color = colorPicker.value;
    if (noteText) {
        notes.push({ text: noteText, category, color });
        chrome.storage.local.set({ notes }, loadNotes);
        noteInput.value = '';
    }
});

// Initialize
loadNotes();