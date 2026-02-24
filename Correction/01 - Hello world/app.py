from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

app = Flask(__name__)

# Configuration SQLAlchemy
engine = create_engine("sqlite:///instance/movies.db", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)

    def __repr__(self):
        return f"<Movie {self.title}>"


@app.route("/", methods=["GET", "POST"])
def index():
    session = Session()
    try:
        if request.method == "POST":
            movie_title = request.form.get("title")
            if movie_title:
                new_movie = Movie(title=movie_title)
                session.add(new_movie)
                session.commit()
            return redirect(url_for("index"))

        movies = session.query(Movie).all()
        return render_template("index.html", movies=movies)
    finally:
        session.close()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    app.run(debug=True)
