# Movie Rating App Documentation

## Overview

The Movie Rating App is a web application designed for browsing and managing a list of movies. It provides CRUD operations for movies and reviews, and it features a user-friendly frontend for easy interaction. It lets user:
* Browse movies and ratings
* Add new movies
* Browse details of movie
* Add rating to movie

## Features

**Authentication:** The app utilizes the Microsoft Identity Platform for secure user authentication.

**Database Connectivity:** It connects to a SQL Server database to store and retrieve movie data.

**Logging and Metrics:** OpenCensus Flask Extension is employed to send logs and metrics to Azure Application Insights, enabling comprehensive monitoring and performance analysis.

**Continuous Integration and Deployment:** GitHub Actions is set up for automated build, test, and deployment processes.

## System architecture
![System architecture](/Architecture.png)
