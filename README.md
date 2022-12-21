Pieter van der Deen - r0667341

# Netflix recommender system (lab1)

This a small example I build for a Netflix recommender system. 
To run the code, first create a volume where the model will be stored

```
docker volume create modelvolume
```

Then create the model in a container:

```
cd model
docker compose up
```

The model is now stored in the volume. Run the UI:

```
docker compose down
cd ../host
docker compose up
```

The interface is now accessable at http://localhost:5005 

# AWS AI app (lab2)

Run the main.py script. Make sure the AWS cli has the right privelages.