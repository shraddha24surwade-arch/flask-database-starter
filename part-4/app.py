"""Part 4: REST API with Flask
===========================
Build a JSON API for database operations (used by frontend apps, mobile apps, etc.)

What You will Learn:
- REST API concepts (GET, POST, PUT, DELETE)
- JSON responses with jsonify
- API error handling
- Status codes
- Testing APIs with curl or Postman

Prerequisites: Complete part-3 (SQLAlchemy)
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# =============================================================================
# MODELS
# =============================================================================

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(  # Foreign Key (Many Books → One Author)
        db.Integer,
        db.ForeignKey('author.id'),
        nullable=False )
    def B_to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'isbn': self.isbn,
            'author': {
                'id': self.author_ref.id,
                'name': self.author_ref.name
            },
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    city = db.Column(db.String(100), nullable=False)
    books = db.relationship(  # One-to-Many relationship
        'Book',
        backref='author_ref',
        lazy=True,
        cascade='all, delete-orphan' )
    def A_to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'books': [book.B_to_dict() for book in self.books]
        }



# =============================================================================
# REST API ROUTES FOR BOOK
# =============================================================================

# GET /api/books - Get all books
@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify({  # Return JSON response
        'success': True,
        'count': len(books),
        'books': [book.B_to_dict() for book in books]  # List comprehension to convert all
    })


# GET /api/books/<id> - Get single book
@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({
            'success': False,
            'error': 'Book not found'
        }), 404  # Return 404 status code

    return jsonify({
        'success': True,
        'book': book.B_to_dict()
    })


# POST /api/books - Create new book
@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()  # Get JSON data from request body

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    if not data.get('title'):
        return jsonify({
            'success': False,
            'error': 'Title required'
        }), 400

    author = Author.query.get(data['author_id'])
    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    # Check for duplicate ISBN
    if data.get('isbn'):
        existing = Book.query.filter_by(isbn=data['isbn']).first()
        if existing:
            return jsonify({'success': False, 'error': 'ISBN already exists'}), 400

    new_book = Book(
        title=data['title'],
        year=data.get('year'),
        isbn=data.get('isbn'),
        author_id=data['author_id']
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book created successfully',
        'book': new_book.B_to_dict()
    }), 201  # 201 = Created


# PUT /api/books/<id> - Update book
@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    # Update fields if provided
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'year' in data:
        book.year = data['year']
    if 'isbn' in data:
        book.isbn = data['isbn']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book updated successfully',
        'book': book.B_to_dict()
    })


# DELETE /api/books/<id> - Delete book
@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book deleted successfully'
    })


# =============================================================================
# REST API ROUTES FOR AUTHOR
# =============================================================================

# GET /api/authors - Get all authors
@app.route('/api/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify({  # Return JSON response
        'success': True,
        'count': len(authors),
        'authors': [author.A_to_dict() for author in authors]  # List comprehension to convert all
    })


# GET /api/authors/<id> - Get single author
@app.route('/api/authors/<int:id>', methods=['GET'])
def get_author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({
            'success': False,
            'error': 'Author not found'
        }), 404  # Return 404 status code

    return jsonify({
        'success': True,
        'author': author.A_to_dict()
    })


# POST /api/authors - Create new author
@app.route('/api/authors', methods=['POST'])
def create_author():
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    if not data.get('name') or not data.get('city'):
        return jsonify({
            'success': False,
            'error': 'Name and city are required'
        }), 400

    existing = Author.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({'success': False, 'error': 'Author already exists'}), 400

    new_author = Author(
        name=data['name'],
        city=data['city']
    )

    db.session.add(new_author)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Author created successfully',
        'author': new_author.A_to_dict()
    }), 201


# PUT /api/authors/<id> - Update author
@app.route('/api/authors/<int:id>', methods=['PUT'])
def update_author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    # Update fields if provided
    if 'name' in data:
        author.name = data['name']
    if 'book_name' in data:
        author.book_name = data['book_name']
    if 'city' in data:
        author.city = data['city']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Author updated successfully',
        'author': author.A_to_dict()
    })


# DELETE /api/authors/<id> - Delete author
@app.route('/api/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    db.session.delete(author)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Author deleted successfully'
    })


# =============================================================================
# BONUS: Search and Filter
# =============================================================================

# GET /api/books/search?q=python&author=john
@app.route('/api/books/search', methods=['GET'])
def search_books():
    query = Book.query.join(Author)

    title = request.args.get('title')
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))

    author = request.args.get('author')
    if author:
        query = query.filter(Author.name.ilike(f'%{author}%'))

    year = request.args.get('year')
    if year:
        query = query.filter(Book.year == int(year))

    books = query.all()

    return jsonify({
        'success': True,
        'count': len(books),
        'books': [book.B_to_dict() for book in books]
    })


# Search Author
@app.route('/api/authors/search', methods=['GET'])
def search_authors():
    query = Author.query.join(Book)

    name = request.args.get('name')
    if name:
        query = query.filter(Author.name.ilike(f'%{name}%'))

    city = request.args.get('city')
    if city:
        query = query.filter(Author.city.ilike(f'%{city}%'))

    title = request.args.get('title')
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))

    authors = query.all()

    return jsonify({
        'success': True,
        'count': len(authors),
        'authors': [author.A_to_dict() for author in authors]
    })

# =============================================================================
# ADD PAGINATION
# =============================================================================
@app.route('/api/books/paginated', methods=['GET'])
def get_books_paginated():
    # Get query params with defaults
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=5, type=int)

    # Paginate query
    pagination = Book.query.order_by(Book.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        'success': True,
        'page': page,
        'per_page': per_page,
        'total_items': pagination.total,
        'total_pages': pagination.pages,
        'books': [book.B_to_dict() for book in pagination.items]
    })


# =============================================================================
# ADD SORTING
# =============================================================================
@app.route('/api/books/sorted', methods=['GET'])
def get_books_sorted():
    # Query params
    sort_field = request.args.get('sort', default='id')
    order = request.args.get('order', default='asc')

    # Allowed columns for sorting
    allowed_sorts = {
        'id': Book.id,
        'title': Book.title,
        'year': Book.year,
        'isbn': Book.isbn,
        'created_at': Book.created_at
    }

    # Validate sort field
    sort_column = allowed_sorts.get(sort_field, Book.id)

    # Apply ordering
    if order.lower() == 'desc':
        query = Book.query.order_by(sort_column.desc())
    else:
        query = Book.query.order_by(sort_column.asc())

    books = query.all()

    return jsonify({
        'success': True,
        'sort': sort_field,
        'order': order,
        'count': len(books),
        'books': [book.B_to_dict() for book in books]
    })


# =============================================================================
# SIMPLE WEB PAGE FOR TESTING
# =============================================================================

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Part 4 - REST API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
            h1 { color: #e94560; }
            .endpoint { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #e94560; }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
            .get { background: #27ae60; }
            .post { background: #f39c12; }
            .put { background: #3498db; }
            .delete { background: #e74c3c; }
            code { background: #0f3460; padding: 2px 6px; border-radius: 3px; }
            pre { background: #0f3460; padding: 15px; border-radius: 8px; overflow-x: auto; }
            a { color: #e94560; }
        </style>
    </head>
    <body>
        <h1>Part 4: REST API Demo</h1>
        <p>This is a JSON API - use curl, Postman, or JavaScript fetch() to test!</p>

        <h2>API Endpoints:</h2>

        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books</code> - Get all books
            <br><a href="/api/books" target="_blank">Try it →</a>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books/&lt;id&gt;</code> - Get single book
        </div>

        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/api/books</code> - Create new book
        </div>

        <div class="endpoint">
            <span class="method put">PUT</span>
            <code>/api/books/&lt;id&gt;</code> - Update book
        </div>

        <div class="endpoint">
            <span class="method delete">DELETE</span>
            <code>/api/books/&lt;id&gt;</code> - Delete book
        </div>

        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books/search?q=&lt;title&gt;&author=&lt;name&gt;</code> - Search books
        </div>

        <h2>Test with curl:</h2>
        <pre>
# Get all books
curl http://localhost:5000/api/books

# Create a book
curl -X POST http://localhost:5000/api/books \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Flask Web Development", "author": "Miguel Grinberg", "year": 2018}'

# Update a book
curl -X PUT http://localhost:5000/api/books/1 \\
  -H "Content-Type: application/json" \\
  -d '{"year": 2023}'

# Delete a book
curl -X DELETE http://localhost:5000/api/books/1
        </pre>
    </body>
    </html>
    '''


# =============================================================================
# INITIALIZE DATABASE WITH SAMPLE DATA
# =============================================================================

def init_db():
    with app.app_context():
        db.create_all()

        if Author.query.count() == 0:
            authors = [
                Author(name='Eric Matthes', city='New York'),
                Author(name='Miguel Grinberg', city='Washington'),
                Author(name='Robert C. Martin', city='London'),
            ]
            db.session.add_all(authors)
            db.session.commit()
            print('Sample authors added!')

        if Book.query.count() == 0:
            eric = Author.query.filter_by(name='Eric Matthes').first()
            miguel = Author.query.filter_by(name='Miguel Grinberg').first()
            robert = Author.query.filter_by(name='Robert C. Martin').first()

            books = [
                Book(
                    title='Python Crash Course', year=2019, isbn='978-1593279288', author_id=eric.id
                ),
                Book(
                    title='Flask Web Development', year=2018, isbn='978-1491991732', author_id=miguel.id
                ),
                Book(
                    title='Clean Code', year=2008, isbn='978-0132350884', author_id=robert.id
                ),
            ]

            db.session.add_all(books)
            db.session.commit()
            print('Sample books added!')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)


# =============================================================================
# REST API CONCEPTS:
# =============================================================================
#
# HTTP Method | CRUD      | Typical Use
# ------------|-----------|---------------------------
# GET         | Read      | Retrieve data
# POST        | Create    | Create new resource
# PUT         | Update    | Update entire resource
# PATCH       | Update    | Update partial resource
# DELETE      | Delete    | Remove resource
#
# =============================================================================
# HTTP STATUS CODES:
# =============================================================================
#
# Code | Meaning
# -----|------------------
# 200  | OK (Success)
# 201  | Created
# 400  | Bad Request (client error)
# 404  | Not Found
# 500  | Internal Server Error
#
# =============================================================================
# KEY FUNCTIONS:
# =============================================================================
#
# jsonify()           - Convert Python dict to JSON response
# request.get_json()  - Get JSON data from request body
# request.args.get()  - Get query parameters (?key=value)
#
# =============================================================================


# =============================================================================
# EXERCISE:
# =============================================================================
#
# 1. Add pagination: `/api/books?page=1&per_page=10`
# 2. Add sorting: `/api/books?sort=title&order=desc`
# 3. Create a simple frontend using JavaScript fetch()
#
# =============================================================================

