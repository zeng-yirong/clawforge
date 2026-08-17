"""
Media Catalog Database Environment API

A media catalog database that systematically organizes and stores metadata for diverse
media types including books, movies, and novels. Supports operations for querying,
updating, and comparing media entries.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE = {
    # Books collection
    "books": {
        "B2941": {
            "book_id": "B2941",
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "genre": "Classic Fiction",
            "publication_year": 1925,
            "isbn": "978-0-7432-7356-5",
            "description": "A story of wealth, love, and the American Dream in the Jazz Age."
        },
        "B1023": {
            "book_id": "B1023",
            "title": "1984",
            "author": "George Orwell",
            "genre": "Dystopian Fiction",
            "publication_year": 1949,
            "isbn": "978-0-452-28423-4",
            "description": "A dystopian novel about totalitarianism and surveillance."
        },
        "B3847": {
            "book_id": "B3847",
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "genre": "Romance",
            "publication_year": 1813,
            "isbn": "978-0-14-143951-8",
            "description": "A romantic novel exploring themes of love, reputation, and class."
        },
        "B5521": {
            "book_id": "B5521",
            "title": "Animal Farm",
            "author": "George Orwell",
            "genre": "Political Satire",
            "publication_year": 1945,
            "isbn": "978-0-452-28424-1",
            "description": "An allegorical novella reflecting events leading to the Russian Revolution."
        }
    },
    
    # Movies collection
    "movies": {
        "M5932": {
            "movie_id": "M5932",
            "title": "Inception",
            "director": "Christopher Nolan",
            "genre": "Science Fiction",
            "release_year": 2010,
            "duration": 148,
            "rating": 4.5,
            "description": "A thief who steals corporate secrets through dream-sharing technology."
        },
        "M2847": {
            "movie_id": "M2847",
            "title": "The Shawshank Redemption",
            "director": "Frank Darabont",
            "genre": "Drama",
            "release_year": 1994,
            "duration": 142,
            "rating": 4.8,
            "description": "Two imprisoned men bond over a number of years, finding solace and redemption."
        },
        "M7621": {
            "movie_id": "M7621",
            "title": "Pulp Fiction",
            "director": "Quentin Tarantino",
            "genre": "Crime",
            "release_year": 1994,
            "duration": 154,
            "rating": 4.3,
            "description": "The lives of two mob hitmen, a boxer, and others intertwine in tales of violence and redemption."
        },
        "M4102": {
            "movie_id": "M4102",
            "title": "The Dark Knight",
            "director": "Christopher Nolan",
            "genre": "Action",
            "release_year": 2008,
            "duration": 152,
            "rating": 4.7,
            "description": "Batman faces the Joker, a criminal mastermind who wants to plunge Gotham into anarchy."
        }
    },
    
    # Novels collection
    "novels": {
        "N3829": {
            "novel_id": "N3829",
            "title": "War and Peace",
            "author": "Leo Tolstoy",
            "genre": "Historical Fiction",
            "publication_year": 1869,
            "description": "An epic novel chronicling Russian society during the Napoleonic Era."
        },
        "N1547": {
            "novel_id": "N1547",
            "title": "Crime and Punishment",
            "author": "Fyodor Dostoevsky",
            "genre": "Psychological Fiction",
            "publication_year": 1866,
            "description": "A psychological drama about a poor ex-student who commits a murder."
        },
        "N6283": {
            "novel_id": "N6283",
            "title": "Don Quixote",
            "author": "Miguel de Cervantes",
            "genre": "Adventure",
            "publication_year": 1605,
            "description": "The adventures of a nobleman who reads too many chivalric romances."
        }
    },
    
    # Reviews collection
    "reviews": {
        "R1001": {
            "review_id": "R1001",
            "movie_id": "M5932",
            "user_id": "U101",
            "rating": 5,
            "comment": "Mind-bending masterpiece! The layers of dreams are brilliantly executed.",
            "timestamp": "2024-01-15T10:30:00"
        },
        "R1002": {
            "review_id": "R1002",
            "movie_id": "M5932",
            "user_id": "U102",
            "rating": 4,
            "comment": "Great visuals and concept, but a bit confusing at times.",
            "timestamp": "2024-01-16T14:22:00"
        },
        "R1003": {
            "review_id": "R1003",
            "movie_id": "M2847",
            "user_id": "U103",
            "rating": 5,
            "comment": "One of the greatest films ever made. Deeply moving.",
            "timestamp": "2024-01-17T09:15:00"
        },
        "R1004": {
            "review_id": "R1004",
            "movie_id": "M7621",
            "user_id": "U101",
            "rating": 4,
            "comment": "Tarantino at his finest. Unique storytelling structure.",
            "timestamp": "2024-01-18T16:45:00"
        }
    },
    
    # Chapters collection
    "chapters": {
        "C001": {
            "chapter_id": "C001",
            "novel_id": "N3829",
            "title": "The Soiree",
            "chapter_number": 1,
            "content_summary": "Introduction to Russian high society at Anna Pavlovna's salon."
        },
        "C002": {
            "chapter_id": "C002",
            "novel_id": "N3829",
            "title": "Prince Andrei's Departure",
            "chapter_number": 2,
            "content_summary": "Prince Andrei prepares to leave for the war against Napoleon."
        },
        "C003": {
            "chapter_id": "C003",
            "novel_id": "N3829",
            "title": "The Battle Begins",
            "chapter_number": 3,
            "content_summary": "The first major military engagement is described in detail."
        },
        "C004": {
            "chapter_id": "C004",
            "novel_id": "N1547",
            "title": "The Crime",
            "chapter_number": 1,
            "content_summary": "Raskolnikov commits the fateful murder that haunts him throughout."
        },
        "C005": {
            "chapter_id": "C005",
            "novel_id": "N1547",
            "title": "The Investigation",
            "chapter_number": 2,
            "content_summary": "Detective Porfiry begins his psychological pursuit of the killer."
        }
    },
    
    # Current user session
    "current_user": {
        "user_id": "U101",
        "username": "media_admin",
        "role": "administrator"
    },
    
    # Session metadata
    "session": {
        "session_id": "sess_abc123",
        "started_at": "2024-01-20T08:00:00",
        "last_activity": "2024-01-20T08:00:00"
    }
}


class MediaCatalogDatabase:
    """
    A media catalog database API for managing books, movies, novels, reviews, and chapters.
    
    This environment provides operations for querying media metadata, adding new entries,
    managing reviews, and organizing novel chapters. It enforces constraints on identifiers
    and ensures data integrity across all media types.
    """
    
    def __init__(self):
        """
        Initialize the MediaCatalogDatabase environment.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
        
        Returns:
            None
        """
        self.books: Dict[str, Dict[str, Any]] = {}
        self.movies: Dict[str, Dict[str, Any]] = {}
        self.novels: Dict[str, Dict[str, Any]] = {}
        self.reviews: Dict[str, Dict[str, Any]] = {}
        self.chapters: Dict[str, Dict[str, Any]] = {}
        self.current_user: Dict[str, Any] = {}
        self.session: Dict[str, Any] = {}
        
        self._api_description = "A media catalog database for organizing and querying books, movies, novels, reviews, and chapters with full CRUD operations."
    
    def _timestamp(self) -> str:
        """
        Generate a standardized ISO format timestamp.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values for the environment.
            long_context: Flag for extended context scenarios (not used in base implementation).
        
        Returns:
            None
        """
        if not scenario:
            scenario = {}
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))
    
    def get_env_state(self) -> Dict[str, Any]:
        """
        Retrieve the complete current state of the environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables:
                - books: Dictionary of all book entries keyed by book_id
                - movies: Dictionary of all movie entries keyed by movie_id
                - novels: Dictionary of all novel entries keyed by novel_id
                - reviews: Dictionary of all review entries keyed by review_id
                - chapters: Dictionary of all chapter entries keyed by chapter_id
                - current_user: Current user session information
                - session: Session metadata
        """
        return {
            "books": deepcopy(self.books),
            "movies": deepcopy(self.movies),
            "novels": deepcopy(self.novels),
            "reviews": deepcopy(self.reviews),
            "chapters": deepcopy(self.chapters),
            "current_user": deepcopy(self.current_user),
            "session": deepcopy(self.session)
        }
    
    # ==================== Query Operations ====================
    
    def get_book_by_id(self, book_id: str) -> Dict[str, Any]:
        """
        Retrieve full metadata of a book using its unique book_id.
        
        Args:
            book_id: The unique identifier for the book (e.g., 'B2941').
        
        Returns:
            Dict[str, Any]: The book metadata if found, or an error dictionary if not found.
        """
        if not book_id:
            return {"error": "book_id is required"}
        
        if book_id not in self.books:
            return {"error": f"Book with id '{book_id}' not found"}
        
        return deepcopy(self.books[book_id])
    
    def get_movie_by_id(self, movie_id: str) -> Dict[str, Any]:
        """
        Retrieve full metadata of a movie using its unique movie_id.
        
        Args:
            movie_id: The unique identifier for the movie (e.g., 'M5932').
        
        Returns:
            Dict[str, Any]: The movie metadata if found, or an error dictionary if not found.
        """
        if not movie_id:
            return {"error": "movie_id is required"}
        
        if movie_id not in self.movies:
            return {"error": f"Movie with id '{movie_id}' not found"}
        
        return deepcopy(self.movies[movie_id])
    
    def get_novel_by_id(self, novel_id: str) -> Dict[str, Any]:
        """
        Retrieve full metadata of a novel using its unique novel_id.
        
        Args:
            novel_id: The unique identifier for the novel (e.g., 'N3829').
        
        Returns:
            Dict[str, Any]: The novel metadata if found, or an error dictionary if not found.
        """
        if not novel_id:
            return {"error": "novel_id is required"}
        
        if novel_id not in self.novels:
            return {"error": f"Novel with id '{novel_id}' not found"}
        
        return deepcopy(self.novels[novel_id])
    
    def get_movie_reviews(self, movie_id: str) -> Dict[str, Any]:
        """
        Retrieve all reviews associated with a given movie_id.
        
        Args:
            movie_id: The unique identifier for the movie.
        
        Returns:
            Dict[str, Any]: Dictionary containing list of reviews for the movie,
                           or an error dictionary if movie not found.
        """
        if not movie_id:
            return {"error": "movie_id is required"}
        
        if movie_id not in self.movies:
            return {"error": f"Movie with id '{movie_id}' not found"}
        
        reviews = [
            deepcopy(review) for review in self.reviews.values()
            if review["movie_id"] == movie_id
        ]
        
        # Sort by timestamp
        reviews.sort(key=lambda x: x["timestamp"])
        
        return {
            "movie_id": movie_id,
            "movie_title": self.movies[movie_id]["title"],
            "review_count": len(reviews),
            "reviews": reviews
        }
    
    def get_novel_chapters(self, novel_id: str) -> Dict[str, Any]:
        """
        Retrieve all chapters belonging to a specified novel_id, returned in chapter number order.
        
        Args:
            novel_id: The unique identifier for the novel.
        
        Returns:
            Dict[str, Any]: Dictionary containing list of chapters sorted by chapter number,
                           or an error dictionary if novel not found.
        """
        if not novel_id:
            return {"error": "novel_id is required"}
        
        if novel_id not in self.novels:
            return {"error": f"Novel with id '{novel_id}' not found"}
        
        chapters = [
            deepcopy(chapter) for chapter in self.chapters.values()
            if chapter["novel_id"] == novel_id
        ]
        
        # Sort by chapter number
        chapters.sort(key=lambda x: x["chapter_number"])
        
        return {
            "novel_id": novel_id,
            "novel_title": self.novels[novel_id]["title"],
            "chapter_count": len(chapters),
            "chapters": chapters
        }
    
    def get_chapter_by_id(self, chapter_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific chapter's details using its unique chapter_id.
        
        Args:
            chapter_id: The unique identifier for the chapter.
        
        Returns:
            Dict[str, Any]: The chapter metadata if found, or an error dictionary if not found.
        """
        if not chapter_id:
            return {"error": "chapter_id is required"}
        
        if chapter_id not in self.chapters:
            return {"error": f"Chapter with id '{chapter_id}' not found"}
        
        return deepcopy(self.chapters[chapter_id])
    
    def get_review_by_id(self, review_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific review using its unique review_id.
        
        Args:
            review_id: The unique identifier for the review.
        
        Returns:
            Dict[str, Any]: The review data if found, or an error dictionary if not found.
        """
        if not review_id:
            return {"error": "review_id is required"}
        
        if review_id not in self.reviews:
            return {"error": f"Review with id '{review_id}' not found"}
        
        return deepcopy(self.reviews[review_id])
    
    def list_books_by_author(self, author: str) -> Dict[str, Any]:
        """
        Retrieve all books written by a specific author.
        
        Args:
            author: The name of the author to search for.
        
        Returns:
            Dict[str, Any]: Dictionary containing list of books by the author.
        """
        if not author:
            return {"error": "author is required"}
        
        books = [
            deepcopy(book) for book in self.books.values()
            if book["author"].lower() == author.lower()
        ]
        
        return {
            "author": author,
            "book_count": len(books),
            "books": books
        }
    
    def list_movies_by_genre(self, genre: str) -> Dict[str, Any]:
        """
        Retrieve all movies in a specified genre.
        
        Args:
            genre: The genre to filter movies by.
        
        Returns:
            Dict[str, Any]: Dictionary containing list of movies in the genre.
        """
        if not genre:
            return {"error": "genre is required"}
        
        movies = [
            deepcopy(movie) for movie in self.movies.values()
            if movie["genre"].lower() == genre.lower()
        ]
        
        return {
            "genre": genre,
            "movie_count": len(movies),
            "movies": movies
        }
    
    def get_media_summary(self) -> Dict[str, Any]:
        """
        Retrieve a high-level count and summary of media items in the catalog.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing counts and summaries for all media types:
                - total_books: Number of books in the catalog
                - total_movies: Number of movies in the catalog
                - total_novels: Number of novels in the catalog
                - total_reviews: Number of reviews in the system
                - total_chapters: Number of chapters across all novels
                - genres: Breakdown of genres across media types
        """
        # Collect all genres
        book_genres = set(book["genre"] for book in self.books.values())
        movie_genres = set(movie["genre"] for movie in self.movies.values())
        novel_genres = set(novel["genre"] for novel in self.novels.values())
        
        return {
            "total_books": len(self.books),
            "total_movies": len(self.movies),
            "total_novels": len(self.novels),
            "total_reviews": len(self.reviews),
            "total_chapters": len(self.chapters),
            "genres": {
                "book_genres": list(book_genres),
                "movie_genres": list(movie_genres),
                "novel_genres": list(novel_genres)
            }
        }
    
    # ==================== State Change Operations ====================
    
    def add_book(
        self,
        book_id: str,
        title: str,
        author: str,
        genre: str,
        publication_year: int,
        isbn: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Add a new book to the catalog with complete metadata.
        
        Args:
            book_id: Unique identifier for the book (must start with 'B').
            title: Title of the book.
            author: Author of the book.
            genre: Genre classification.
            publication_year: Year of publication.
            isbn: ISBN number.
            description: Brief description of the book.
        
        Returns:
            Dict[str, Any]: Success status with book data, or error dictionary.
        """
        # Validate required fields are not null/empty
        if not book_id:
            return {"error": "book_id is required and cannot be null"}
        if not title:
            return {"error": "title is required and cannot be null"}
        if not author:
            return {"error": "author is required and cannot be null"}
        if not genre:
            return {"error": "genre is required and cannot be null"}
        if publication_year is None:
            return {"error": "publication_year is required and cannot be null"}
        if not isbn:
            return {"error": "isbn is required and cannot be null"}
        if not description:
            return {"error": "description is required and cannot be null"}
        
        # Validate book_id prefix
        if not book_id.startswith("B"):
            return {"error": "book_id must start with 'B'"}
        
        # Check for duplicate ID
        if book_id in self.books:
            return {"error": f"Book with id '{book_id}' already exists"}
        
        # Create book entry
        book = {
            "book_id": book_id,
            "title": title,
            "author": author,
            "genre": genre,
            "publication_year": publication_year,
            "isbn": isbn,
            "description": description
        }
        
        self.books[book_id] = book
        
        return {
            "success": True,
            "message": f"Book '{title}' added successfully",
            "book": deepcopy(book)
        }
    
    def add_movie(
        self,
        movie_id: str,
        title: str,
        director: str,
        genre: str,
        release_year: int,
        duration: int,
        rating: float,
        description: str
    ) -> Dict[str, Any]:
        """
        Add a new movie to the catalog with complete metadata.
        
        Args:
            movie_id: Unique identifier for the movie (must start with 'M').
            title: Title of the movie.
            director: Director of the movie.
            genre: Genre classification.
            release_year: Year of release.
            duration: Duration in minutes.
            rating: Initial rating (0-5).
            description: Brief description of the movie.
        
        Returns:
            Dict[str, Any]: Success status with movie data, or error dictionary.
        """
        # Validate required fields
        if not movie_id:
            return {"error": "movie_id is required and cannot be null"}
        if not title:
            return {"error": "title is required and cannot be null"}
        if not director:
            return {"error": "director is required and cannot be null"}
        if not genre:
            return {"error": "genre is required and cannot be null"}
        if release_year is None:
            return {"error": "release_year is required and cannot be null"}
        if duration is None:
            return {"error": "duration is required and cannot be null"}
        if rating is None:
            return {"error": "rating is required and cannot be null"}
        if not description:
            return {"error": "description is required and cannot be null"}
        
        # Validate movie_id prefix
        if not movie_id.startswith("M"):
            return {"error": "movie_id must start with 'M'"}
        
        # Check for duplicate ID
        if movie_id in self.movies:
            return {"error": f"Movie with id '{movie_id}' already exists"}
        
        # Validate rating range
        if not (0 <= rating <= 5):
            return {"error": "rating must be between 0 and 5"}
        
        # Create movie entry
        movie = {
            "movie_id": movie_id,
            "title": title,
            "director": director,
            "genre": genre,
            "release_year": release_year,
            "duration": duration,
            "rating": rating,
            "description": description
        }
        
        self.movies[movie_id] = movie
        
        return {
            "success": True,
            "message": f"Movie '{title}' added successfully",
            "movie": deepcopy(movie)
        }
    
    def add_novel(
        self,
        novel_id: str,
        title: str,
        author: str,
        genre: str,
        publication_year: int,
        description: str
    ) -> Dict[str, Any]:
        """
        Add a new novel to the catalog with complete metadata.
        
        Args:
            novel_id: Unique identifier for the novel (must start with 'N').
            title: Title of the novel.
            author: Author of the novel.
            genre: Genre classification.
            publication_year: Year of publication.
            description: Brief description of the novel.
        
        Returns:
            Dict[str, Any]: Success status with novel data, or error dictionary.
        """
        # Validate required fields
        if not novel_id:
            return {"error": "novel_id is required and cannot be null"}
        if not title:
            return {"error": "title is required and cannot be null"}
        if not author:
            return {"error": "author is required and cannot be null"}
        if not genre:
            return {"error": "genre is required and cannot be null"}
        if publication_year is None:
            return {"error": "publication_year is required and cannot be null"}
        if not description:
            return {"error": "description is required and cannot be null"}
        
        # Validate novel_id prefix
        if not novel_id.startswith("N"):
            return {"error": "novel_id must start with 'N'"}
        
        # Check for duplicate ID
        if novel_id in self.novels:
            return {"error": f"Novel with id '{novel_id}' already exists"}
        
        # Create novel entry
        novel = {
            "novel_id": novel_id,
            "title": title,
            "author": author,
            "genre": genre,
            "publication_year": publication_year,
            "description": description
        }
        
        self.novels[novel_id] = novel
        
        return {
            "success": True,
            "message": f"Novel '{title}' added successfully",
            "novel": deepcopy(novel)
        }
    
    def add_review(
        self,
        review_id: str,
        movie_id: str,
        user_id: str,
        rating: int,
        comment: str
    ) -> Dict[str, Any]:
        """
        Add a user review for a movie.
        
        Args:
            review_id: Unique identifier for the review (must start with 'R').
            movie_id: ID of the movie being reviewed (must exist).
            user_id: ID of the user submitting the review.
            rating: Rating from 1-5.
            comment: Review comment text.
        
        Returns:
            Dict[str, Any]: Success status with review data, or error dictionary.
        """
        # Validate required fields
        if not review_id:
            return {"error": "review_id is required and cannot be null"}
        if not movie_id:
            return {"error": "movie_id is required and cannot be null"}
        if not user_id:
            return {"error": "user_id is required and cannot be null"}
        if rating is None:
            return {"error": "rating is required and cannot be null"}
        if not comment:
            return {"error": "comment is required and cannot be null"}
        
        # Validate review_id prefix
        if not review_id.startswith("R"):
            return {"error": "review_id must start with 'R'"}
        
        # Check if movie exists (constraint: reviews can only be for existing movies)
        if movie_id not in self.movies:
            return {"error": f"Cannot add review: Movie with id '{movie_id}' does not exist"}
        
        # Check for duplicate review ID
        if review_id in self.reviews:
            return {"error": f"Review with id '{review_id}' already exists"}
        
        # Validate rating range
        if not (1 <= rating <= 5):
            return {"error": "rating must be between 1 and 5"}
        
        # Create review entry
        review = {
            "review_id": review_id,
            "movie_id": movie_id,
            "user_id": user_id,
            "rating": rating,
            "comment": comment,
            "timestamp": self._timestamp()
        }
        
        self.reviews[review_id] = review
        
        return {
            "success": True,
            "message": f"Review added for movie '{self.movies[movie_id]['title']}'",
            "review": deepcopy(review)
        }
    
    def add_chapter(
        self,
        chapter_id: str,
        novel_id: str,
        title: str,
        chapter_number: int,
        content_summary: str
    ) -> Dict[str, Any]:
        """
        Add a chapter to a novel.
        
        Args:
            chapter_id: Unique identifier for the chapter (must start with 'C').
            novel_id: ID of the novel this chapter belongs to (must exist).
            title: Title of the chapter.
            chapter_number: Chapter number (must be unique within the novel).
            content_summary: Summary of the chapter content.
        
        Returns:
            Dict[str, Any]: Success status with chapter data, or error dictionary.
        """
        # Validate required fields
        if not chapter_id:
            return {"error": "chapter_id is required and cannot be null"}
        if not novel_id:
            return {"error": "novel_id is required and cannot be null"}
        if not title:
            return {"error": "title is required and cannot be null"}
        if chapter_number is None:
            return {"error": "chapter_number is required and cannot be null"}
        if not content_summary:
            return {"error": "content_summary is required and cannot be null"}
        
        # Validate chapter_id prefix
        if not chapter_id.startswith("C"):
            return {"error": "chapter_id must start with 'C'"}
        
        # Check if novel exists
        if novel_id not in self.novels:
            return {"error": f"Cannot add chapter: Novel with id '{novel_id}' does not exist"}
        
        # Check for duplicate chapter ID
        if chapter_id in self.chapters:
            return {"error": f"Chapter with id '{chapter_id}' already exists"}
        
        # Check for unique chapter number within the novel
        for chapter in self.chapters.values():
            if chapter["novel_id"] == novel_id and chapter["chapter_number"] == chapter_number:
                return {"error": f"Chapter number {chapter_number} already exists in novel '{novel_id}'"}
        
        # Create chapter entry
        chapter = {
            "chapter_id": chapter_id,
            "novel_id": novel_id,
            "title": title,
            "chapter_number": chapter_number,
            "content_summary": content_summary
        }
        
        self.chapters[chapter_id] = chapter
        
        return {
            "success": True,
            "message": f"Chapter '{title}' added to novel '{self.novels[novel_id]['title']}'",
            "chapter": deepcopy(chapter)
        }
    
    def update_book(
        self,
        book_id: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        publication_year: Optional[int] = None,
        isbn: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing book's information.
        
        Args:
            book_id: The unique identifier for the book.
            title: Optional new title.
            author: Optional new author.
            genre: Optional new genre.
            publication_year: Optional new publication year.
            isbn: Optional new ISBN.
            description: Optional new description.
            
        Returns:
            Dict[str, Any]: Success status with updated book data, or error dictionary.
        """
        if book_id not in self.books:
            return {"error": f"Book with ID '{book_id}' not found"}
        
        book = self.books[book_id]
        
        if title is not None:
            book["title"] = title
        if author is not None:
            book["author"] = author
        if genre is not None:
            book["genre"] = genre
        if publication_year is not None:
            book["publication_year"] = publication_year
        if isbn is not None:
            book["isbn"] = isbn
        if description is not None:
            book["description"] = description
        
        return {
            "success": True,
            "message": f"Book '{book_id}' updated successfully",
            "book": deepcopy(book)
        }
    
    def delete_book(self, book_id: str) -> Dict[str, Any]:
        """
        Delete a book from the library.
        
        Args:
            book_id: The unique identifier for the book.
            
        Returns:
            Dict[str, Any]: Success status with deleted book data, or error dictionary.
        """
        if book_id not in self.books:
            return {"error": f"Book with ID '{book_id}' not found"}
        
        deleted_book = self.books.pop(book_id)
        
        return {
            "success": True,
            "message": f"Book '{deleted_book['title']}' deleted successfully",
            "deleted_book": deleted_book
        }
    
    def search_books(
        self,
        query: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for books based on various criteria.
        
        Args:
            query: Optional text to search in title or description.
            author: Optional author name to filter by.
            genre: Optional genre to filter by.
            year_from: Optional minimum publication year.
            year_to: Optional maximum publication year.
            
        Returns:
            Dict[str, Any]: Dictionary containing search results and count.
        """
        results = []
        
        for book in self.books.values():
            match = True
            
            if query is not None:
                query_lower = query.lower()
                if not (query_lower in book["title"].lower() or 
                        query_lower in book.get("description", "").lower()):
                    match = False
            
            if author is not None and author.lower() not in book["author"].lower():
                match = False
            
            if genre is not None and book.get("genre", "").lower() != genre.lower():
                match = False
            
            if year_from is not None and book.get("publication_year", 0) < year_from:
                match = False
            
            if year_to is not None and book.get("publication_year", 9999) > year_to:
                match = False
            
            if match:
                results.append(deepcopy(book))
        
        return {
            "success": True,
            "count": len(results),
            "books": results
        }
    
    def get_novel_with_chapters(self, novel_id: str) -> Dict[str, Any]:
        """
        Get a novel with all its chapters.
        
        Args:
            novel_id: The unique identifier for the novel.
            
        Returns:
            Dict[str, Any]: Success status with novel and chapter data, or error dictionary.
        """
        if novel_id not in self.novels:
            return {"error": f"Novel with ID '{novel_id}' not found"}
        
        novel = deepcopy(self.novels[novel_id])
        chapters = [
            deepcopy(ch) for ch in self.chapters.values() 
            if ch["novel_id"] == novel_id
        ]
        chapters.sort(key=lambda x: x["chapter_number"])
        
        novel["chapters"] = chapters
        
        return {
            "success": True,
            "novel": novel
        }
    
    def list_all_books(self) -> Dict[str, Any]:
        """
        List all books in the library.
        
        Args:
            None
            
        Returns:
            Dict[str, Any]: Dictionary containing list of all books and count.
        """
        return {
            "success": True,
            "count": len(self.books),
            "books": [deepcopy(book) for book in self.books.values()]
        }
    
    def list_all_novels(self) -> Dict[str, Any]:
        """
        List all novels in the library.
        
        Args:
            None
            
        Returns:
            Dict[str, Any]: Dictionary containing list of all novels and count.
        """
        return {
            "success": True,
            "count": len(self.novels),
            "novels": [deepcopy(novel) for novel in self.novels.values()]
        }


__TEST_CASES__ = [
    {
        "name": "test_add_book",
        "input": {
            "method": "add_book",
            "params": {
                "book_id": "B9999",
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "genre": "Fiction",
                "publication_year": 1925,
                "isbn": "978-0743273565",
                "description": "A classic American novel."
            }
        },
        "expected": {
            "success": True
        }
    },
    {
        "name": "test_add_novel",
        "input": {
            "method": "add_novel",
            "params": {
                "novel_id": "N9999",
                "title": "War and Peace",
                "author": "Leo Tolstoy",
                "genre": "Historical Fiction",
                "publication_year": 1869,
                "description": "An epic novel about Russian society."
            }
        },
        "expected": {
            "success": True
        }
    },
    {
        "name": "test_update_book",
        "input": {
            "method": "update_book",
            "params": {
                "book_id": "B2941",
                "title": "The Great Gatsby - Revised Edition",
                "description": "A classic American novel updated."
            }
        },
        "expected": {
            "success": True
        }
    },
    {
        "name": "test_get_novel_with_chapters",
        "input": {
            "method": "get_novel_with_chapters",
            "params": {
                "novel_id": "N3829"
            }
        },
        "expected": {
            "success": True
        }
    },
    {
        "name": "test_book_not_found",
        "input": {
            "method": "update_book",
            "params": {
                "book_id": "nonexistent_book",
                "title": "New Title"
            }
        },
        "expected": {
            "error": "Book with ID 'nonexistent_book' not found"
        }
    }
]