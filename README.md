# Recommender Systems

![image](https://github.com/user-attachments/assets/1c9747cc-9fff-41c0-95ef-3660e5b52afc)

## Project Description:
The goal of the concluding project is to experiment with different strategies to generate recommendations of similar items. The movie domain can be used for this experiment. 

Generally, similar item recommendations can be found on many websites, including video streaming sites. It is, however, not always immediately clear when we should consider two movies to be similar. It could be because they have the same actors, the same director, similar plot descriptions, the same genre, or even a similar movie cover. A recent research work on the topic can be found here: https://web-ainf.aau.at/pub/jannach/files/Journal_UMUAI_2019-2.pdf

The first task in this project is to develop a number of (at least 5) functions in Python that, given a reference movie ID, return a ranked list of the top-5 most similar items. Each function has to implement a different strategy. For the experiment, you can use the MovieLens 20M (or a smaller) dataset, which also contains some content information, see: https://grouplens.org/datasets/movielens/

In addition, a number of additional movie features can be found here: https://drive.google.com/file/d/1je77e0Lq8naVUsjoOzk5RuI2H3ceHlSz/view )(500 MB) This zip file contains a number of JSON-files, each file containing additional data for a given movie (but no ratings). The MovieLens dataset can be combined with this dataset based on the field “movielensID”. In this dataset, many of the URLs pointing to the movie poster images are outdated. An alternative dataset with posters for the movies can be found here: https://www.kaggle.com/ghrzarea/movielens-20m-posters-for-machine-learning

Next, implement a user interface, where the reference movie can be searched by title. The user can then select one of the returned search results and the system then presents five lists, each one containing similar movie recommendations. Each list is based on one of the implemented similarity functions.

The user interface has to be web-based (e.g., using the Django framework) and it has to be designed in a way that it is reasonably easy to use in terms of searching, movie selection, and the analysis of the results.

The final task lies in the evaluation of the different strategies. Try out at least 20 movies from different genres and manually inspect the different result lists. Write a short report that summarizes the observations. Possible contents could be: Which recommendation method led to the best results? Which method led to surprises? Which method led to poor or unexpected results etc.

## Project planning / important dates:
- Intermediate meeting (20.05.2025): Each project team presents an update on the current state of their design and implementation of the project. Presentation time per team is 20 minutes.
- Final meeting (24.06.2025): Each project team presents their final software solution and the outcomes of their analyses. Presentation time per team is 30 minutes max.
- Final deadline (15.07.2025): Deadline for submitting the project code including light documentation and the report by email to dietmar.jannach@aau.at

## Requirements & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Kirschzelle/recommender_systems.git
cd recommender_systems/movie_recommender
```

### Step 2: Dataset Setup

Ensure the following folder structure is present in the root `movie_recommender/` directory:

```
movie_recommender/
└── datasets/
    ├── information/   # Rename downloaded folder to 'information'
    └── posters/       # Rename downloaded folder to 'posters'
```

- Download `information/` data from [Google Drive](https://drive.google.com/file/d/1je77e0Lq8naVUsjoOzk5RuI2H3ceHlSz/view) and rename the folder to `information`.
- Download `posters/` data from [Kaggle](https://www.kaggle.com/ghrzarea/movielens-20m-posters-for-machine-learning) and rename the folder to `posters`.
- Download `ml-20m` data from [Movielens](https://grouplens.org/datasets/movielens/).
- **Do not delete `0.png`** in the `posters/` folder — it is used as a fallback image.

### Step 3: Python Version

Ensure you're using **Python 3.10.3**. Other versions, especially on macOS, may cause issues.

### Step 4: Install Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

### Step 5: Run Django Setup

Run the following commands to apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Run the Full Pipeline

```bash
python manage.py run_all
```

This will prompt you to delete all existing movies. Type 'yes'.
If you want to fetch missing movie posters from the internet, do the following:

1. Export your TMDB API key:

```bash
export TMDB_API_KEY=your_api_key_here
```

2. Then run:

```bash
python manage.py run_all --fetch-posters
```

> Note: Enabling `--fetch-posters` will significantly increase the time it takes to build the database.

### Alternative: Run Video Import only.

Be advised that for quick testing of your own specific algorithm you can skip the computations for the image algorithm. In this case run the following:
```bash
python manage.py import-videos
```

> Note: You can use `--clear` to remove previous imports before running the import.

### Step 7: Start the Server

```bash
python manage.py runserver
```

The application will now be accessible at `http://127.0.0.1:8000/`.
