const API = 'http://127.0.0.1:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    loadAuthors();
    loadBooks();
    loadAuthorDropdown();
});

/* ================= AUTHORS ================= */
function renderAuthors(authors) {
    const table = document.getElementById('authorsTable');
    table.innerHTML = '';

    if (!authors || authors.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="6" style="text-align:center;">No authors found</td>
            </tr>
        `;
        return;
    }

    authors.forEach(a => {

        const bookTitles = a.books.length
                    ? a.books.map(b => b.title).join(', ')
                    : '—';

        table.innerHTML += `
            <tr>
                <td>${a.id}</td>
                <td>${a.name}</td>
                <td>${a.city}</td>
                <td>${bookTitles}</td>
                <td>
                    <button class="edit"
                        onclick="editAuthor(${a.id}, '${a.name}', '${a.city}')">
                        Edit
                    </button>
                    <button class="delete" onclick="deleteAuthor(${a.id})">
                        Delete
                    </button>
                </td>
            </tr>
        `;
    });
}


function loadAuthors() {
    fetch(`${API}/authors`)
        .then(res => res.json())
        .then(data => {
            renderAuthors(data.authors);
        });
}

function loadAuthorDropdown() {
    const select = document.getElementById('authorSelect');
    if (!select) return;
    fetch(`${API}/authors`)
        .then(res => res.json())
        .then(data => {
            select.innerHTML = '<option value="">-- Select Author --</option>';
            data.authors.forEach(author => {
                const option = document.createElement('option');
                option.value = author.id;
                option.textContent = author.name;
                select.appendChild(option);
            });
        })
        .catch(err => console.error('Author dropdown error:', err));
}

function saveAuthor() {
    const id = document.getElementById('authorId').value;
    const payload = {
        name: document.getElementById('authorName').value,
        city: document.getElementById('authorCity').value
    };
    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API}/authors/${id}` : `${API}/authors`;
    fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).then(() => {
        resetAuthorForm();
        loadAuthors();
        loadAuthorDropdown();
    });
}



function editAuthor(id, name, city) {
    document.getElementById('authorId').value = id;
    document.getElementById('authorName').value = name;
    document.getElementById('authorCity').value = city;
}

function deleteAuthor(id) {
    fetch(`${API}/authors/${id}`, { method: 'DELETE' })
        .then(() => {
            loadAuthors();
            loadBooks();
        });
}

function resetAuthorForm() {
    document.getElementById('authorId').value = '';
    document.getElementById('authorName').value = '';
    document.getElementById('authorCity').value = '';
}

/* ================= BOOKS ================= */
function renderBooks(books) {
    const table = document.getElementById('booksTable');
    table.innerHTML = '';

    if (!books || books.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="6" style="text-align:center;">No books found</td>
            </tr>
        `;
        return;
    }

    books.forEach(b => {
        table.innerHTML += `
            <tr>
                <td>${b.id}</td>
                <td>${b.title}</td>
                <td>${b.year || ''}</td>
                <td>${b.isbn || ''}</td>
                <td>${b.author.name}</td>
                <td>
                    <button class="edit"
                        onclick="editBook(${b.id}, '${b.title}', '${b.year}', '${b.isbn}', ${b.author.id})">
                        Edit
                    </button>
                    <button class="delete" onclick="deleteBook(${b.id})">
                        Delete
                    </button>
                </td>
            </tr>
        `;
    });
}

function loadBooks() {
    fetch(`${API}/books`)
        .then(res => res.json())
        .then(data => {
            renderBooks(data.books);
        });
}

function saveBook() {
    const id = document.getElementById('bookId').value;
    const payload = {
        title: document.getElementById('bookTitle').value,
        year: document.getElementById('bookYear').value,
        isbn: document.getElementById('bookIsbn').value,
        author_id: document.getElementById('authorSelect').value
    };

    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API}/books/${id}` : `${API}/books`;

    fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).then(() => {
        resetBookForm();
        loadBooks();
    });
}

function editBook(id, title, year, isbn, authorId) {
    document.getElementById('bookId').value = id;
    document.getElementById('bookTitle').value = title;
    document.getElementById('bookYear').value = year;
    document.getElementById('bookIsbn').value = isbn;
    document.getElementById('authorSelect').value = authorId;
}

function deleteBook(id) {
    fetch(`${API}/books/${id}`, { method: 'DELETE' })
        .then(() => loadBooks());
}

function resetBookForm() {
    document.getElementById('bookId').value = '';
    document.getElementById('bookTitle').value = '';
    document.getElementById('bookYear').value = '';
    document.getElementById('bookIsbn').value = '';
}

function searchBooks() {
    const title = document.getElementById('searchTitle').value.trim();
    const author = document.getElementById('searchAuthor').value.trim();
    const year = document.getElementById('searchYear').value.trim();

    let url = `${API}/books/search?`;

    if (title) url += `title=${encodeURIComponent(title)}&`;
    if (author) url += `author=${encodeURIComponent(author)}&`;
    if (year) url += `year=${encodeURIComponent(year)}&`;

    // clean trailing &
    url = url.endsWith('&') ? url.slice(0, -1) : url;

    fetch(url)
        .then(res => res.json())
        .then(data => {
            renderBooks(data.books);
        })
        .catch(err => console.error('Search error:', err));
}


function clearBookSearch() {
    document.getElementById('searchTitle').value = '';
    document.getElementById('searchAuthor').value = '';
    document.getElementById('searchYear').value = '';
    loadBooks();   // reload full list
}


function searchAuthors() {
    const name = document.getElementById('searchName').value.trim();
    const city = document.getElementById('searchCity').value.trim();
    const book = document.getElementById('searchAuthorBook').value.trim();

    let url = `${API}/authors/search?`;

    if (name) url += `name=${encodeURIComponent(name)}&`;
    if (city) url += `city=${encodeURIComponent(city)}&`;
    if (book) url += `title=${encodeURIComponent(book)}&`;

    url = url.endsWith('&') ? url.slice(0, -1) : url;

    fetch(url)
        .then(res => res.json())
        .then(data => renderAuthors(data.authors))
        .catch(err => console.error(err));
}


function clearAuthorSearch() {
    document.getElementById('searchName').value = '';
    document.getElementById('searchCity').value = '';
    document.getElementById('searchAuthorBook').value = '';
    loadAuthors();   
}


function showSection(section) {
    document.getElementById('authorsSection').style.display =
        section === 'authors' ? 'block' : 'none';

    document.getElementById('booksSection').style.display =
        section === 'books' ? 'block' : 'none';

    document.querySelectorAll('.nav-btn').forEach(btn =>
        btn.classList.remove('active')
    );

    if (section === 'authors') {
        document.querySelector('.nav-btn:nth-child(1)').classList.add('active');
        loadAuthors();
    } else {
        document.querySelector('.nav-btn:nth-child(2)').classList.add('active');
        loadBooks();
        loadAuthors(); // needed for author dropdown
    }
}
