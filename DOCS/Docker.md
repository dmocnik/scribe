(This is placeholder info for now)

### Workflow (Run this in project root)
```sudo docker builder prune``` (prune unused builders)
```sudo docker image prune -a``` (prune unused images)
```sudo docker-compose build --no-cache``` (build the image)
```sudo docker-compose up``` (run the image in the foreground)

### Alternative Workflow (Run this in project root)
```sudo docker-compose up --build``` (build and run the image in the foreground)
