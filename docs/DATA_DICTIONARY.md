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
