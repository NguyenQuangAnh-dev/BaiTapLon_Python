# Data Dictionary

## Project

Football Data Analysis – Season 2024/2025

## Purpose

This document defines the common data schema used by all
scrapers, preprocessing modules, analysis modules, and the final pipeline.

## Core Tables

- players
- teams
- player_stats
- team_stats
- matches
- transfers
## 1. players

| Column        | Type   | Required | Description                     |
|---------------|--------|----------|---------------------------------|
| player_id     | string | YES      | Unique identifier of the player |
| player_name   | string | YES      | Full name of the player         |
| date_of_birth | date   | NO       | Player's date of birth          |
| nationality   | string | NO       | Player's nationality            |
| position      | string | NO       | Main playing position           |
| team_id       | string | YES      | ID of the player's team         |
## 2. teams

| Column | Type | Required | Description |
|---|---|---|---|
| team_id | string | YES | Unique identifier of the team |
| team_name | string | YES | Full name of the team |
| league | string | YES | League in which the team competes |
| country | string | YES | Country of the league |
## 3. player_stats
|Column| Type| Required | Description|
|---|---|---|---|
|player_id|string|YES|ID of the player |
| season | string | YES | Season of the statistics |
| matches | int | NO | Number of matches played |
| starts | int | NO | Number of matches started |
| minutes | int | NO | Total minutes played |
| goals | int | NO | Number of goals scored |
| assists | int | NO | Number of assists |
| shots | int | NO | Total shots |
| shots_on_target | int | NO | Shots on target |
| passes | int | NO | Total passes attempted |
| key_passes | int | NO | Passes creating a shooting opportunity |
| pass_accuracy | float | NO | Passing accuracy percentage |
| tackles | int | NO | Number of tackles |
| interceptions | int | NO | Number of interceptions |
| clearances | int | NO | Number of clearances |
| blocks | int | NO | Number of blocked shots or passes |
| duels_won | int | NO | Number of duels won |
| yellow_cards | int | NO | Number of yellow cards |
| red_cards | int | NO | Number of red cards |
## 4. team_stats

| Column | Type | Required | Description |
|---|---|---|---|
| team_id | string | YES | ID of the team |
| season | string | YES | Season of the statistics |
| matches | int | NO | Number of matches played |
| wins | int | NO | Number of matches won |
| draws | int | NO | Number of matches drawn |
| losses | int | NO | Number of matches lost |
| goals_for | int | NO | Total goals scored |
| goals_against | int | NO | Total goals conceded |
| goal_difference | int | NO | Goals scored minus goals conceded |
| points | int | NO | Total league points |
| clean_sheets | int | NO | Number of matches without conceding a goal |
| possession | float | NO | Average possession percentage |
| shots | int | NO | Total shots |
| shots_on_target | int | NO | Total shots on target |
## 5. matches

| Column | Type | Required | Description |
|---|---|---|---|
| match_id | string | YES | Unique identifier of the match |
| date | date | YES | Date when the match was played |
| league | string | YES | League of the match |
| season | string | YES | Season of the match |
| home_team_id | string | YES | ID of the home team |
| away_team_id | string | YES | ID of the away team |
| home_score | int | YES | Goals scored by the home team |
| away_score | int | YES | Goals scored by the away team |
| result | string | YES | Match result: H, D, or A |
