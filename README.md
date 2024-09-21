# Social Application

## Overview
Social Application that allows users to connect with friends, send friend requests, and manage user interactions such as blocking and searching users.

## Features
- User registration and authentication
- Sending , accepting and rejecting friend requests
- Blocking and unblocking users
- Searching for users by email or name
- Pagination for user lists

## Tech Stack
- **Backend**: Django, Django Rest Framework
- **Database**: PostgreSQL
- **Authentication**: JWT
- **Deployment**: Docker

## Installation

### Steps
1. Clone the repository:
   ```bash
   git clone git@github.com:kirannadimpalli/social_application.git
   cd social_application
   ```

2. Create a virtual environment and activate it
    ```bash
    python -m venv myenv
    source myenv/bin/activate
    ```





# API Documentation

## Authentication

- POST /api/login/: Login and obtain a token.
- POST /api/signup/: Register a new user.
## User Management
- GET /api/users/search_users/: Search users by email or name.
- POST /api/users/block_user/: Block a user.
- POST /api/users/unblock_user/: unBlock a user.
- GET /api/users/list_pending_requests/: List pending friend requests.
- GET /api/users/list_friends/: List accepted friend.
## Friend Management
- POST /api/send_friend_request/: Send a friend request.
- POST /api/accept_friend_request: Accept a friend request.
- POST /api/reject_friend_request: Reject a friend request.

## Postman API Collection

To test the APIs for this project using Postman, you can import the Postman collection provided in this repository:

1. Download the Postman collection: [social_app_postman_collection.json](./postman-collection/social_app_postman_collection.json)
2. Open Postman and click on **Import**.
3. Choose the downloaded JSON file to import all the available APIs.

