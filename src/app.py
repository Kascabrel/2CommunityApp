from src import create_app

app = create_app( development= True)
if __name__ == "__main__":
    app.run(debug=True)
