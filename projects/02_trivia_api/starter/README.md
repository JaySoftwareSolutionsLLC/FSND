# Full Stack API Final Project

# FSND Trivia App
The primary function of this application is a quiz that prompts the user with a set # of questions (optionally based on a specific category) until either there are no un-asked questions remaining, or until an established number of questions have been asked (whichever comes first). The GUI also allows users to view all categories, view all questions, view all questions of a specific category, create new questions, and delete questions. With this CRUD functionality, users can customize the application to their liking and quiz themselves as they see fit.

# FSND Trivia API

## Description
The FSND Trivia API allows communication with the trivia database. Endpoints exist to retrieve categories and paginated question sets (optionally filtered by a category), create new questions, as well as delete questions. Any origin can make these requests and no special key or ID is necessary for authentication.

## Best Practices
- Variables & Function names should be clear. Preference for clarity over conciseness.
- Endpoints should be logically named.
- Code should be commented where appropriate. If it would not be clear to a newly onboarded intern what is happening, then comments must be added.

## Errors
This API uses conventional HTTP response codes to indicate the success or failute of an API request. All endpoints are formatted to respond with a success (200) code if the request is to an established endpoint. If the request has incorrect or insufficient body/request parameters then the response should be a successful (200) JSON object with "success":False.

## Endpoints
### **Categories**
#### GET
Endpoint: /api/categories
Functionality: Returns a JSON response of all categories from application database, a success boolean, and a count of total categories.
Example Response:
```JSON
{
  "categories": [
    {
      "id": 1,
      "type": "Science"
    },
    {
      "id": 2,
      "type": "Art"
    },
    {
      "id": 3,
      "type": "Geography"
    },
    {
      "id": 4,
      "type": "History"
    },
    {
      "id": 5,
      "type": "Entertainment"
    },
    {
      "id": 6,
      "type": "Sports"
    }
  ],
  "success": true,
  "total_categories": 6
}
```

### **Questions**
#### GET
Endpoint: api/questions
Query Params: page (int | optional)
Functionality: Returns a JSON response of all categories and paginated questions from application database, a success boolean, and a count of total questions.
Example Response:
```JSON
{
  "categories": [
    {
      "id": 1,
      "type": "Science"
    },
    {
      "id": 2,
      "type": "Art"
    },
    {
      "id": 3,
      "type": "Geography"
    },
    {
      "id": 4,
      "type": "History"
    },
    {
      "id": 5,
      "type": "Entertainment"
    },
    {
      "id": 6,
      "type": "Sports"
    }
  ],
  "questions": [
    {
      "answer": "Scientific Method",
      "category": 1,
      "difficulty": 1,
      "id": 29,
      "question": "What is the name of the method used in Science?"
    },
    {
      "answer": "Soccer",
      "category": 6,
      "difficulty": 2,
      "id": 31,
      "question": "What sport is played primarily with feet"
    },
    {
      "answer": "1912",
      "category": 4,
      "difficulty": 3,
      "id": 32,
      "question": "What year did the Titanic Sink"
    }
  ],
  "success": true,
  "total_questions": 23
}
```
Endpoint: /api/categories/<int:category_id>/questions
Functionality: Returns all questions relating to the category_id category
Example Response:
```JSON
{
  "currentCategory": "4",
  "questions": [
    {
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2,
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    },
    {
      "answer": "Muhammad Ali",
      "category": 4,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?"
    },
    {
      "answer": "George Washington Carver",
      "category": 4,
      "difficulty": 2,
      "id": 12,
      "question": "Who invented Peanut Butter?"
    },
    {
      "answer": "Scarab",
      "category": 4,
      "difficulty": 4,
      "id": 23,
      "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    }
  ],
  "success": true,
  "total_questions": 4
}
```
#### POST
Endpoint: /api/questions
Functionality: Creates a new question and persists it to database. Returns the request and a success boolean.
Example Request:
```JSON
{
    "question": "What year did the Titanic Sink",
    "answer": "1912",
    "category": 4,
    "difficulty": 3
}
```
Example Response:
```JSON
{
  "request": {
    "answer": "1912",
    "category": 4,
    "difficulty": 3,
    "id": null,
    "question": "What year did the Titanic Sink"
  },
  "success": true
}
```
Endpoint: /api/questions/search
Functionality: Returns a list of questions whose question contains the requested searchTerm. Also returns a success boolean and the total number of questions that match search criteria.
Example Request:
```JSON
{
	"searchTerm" : "Who"
}
```
Example Response:
```JSON
{
  "questions": [
    {
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2,
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    },
    {
      "answer": "George Washington Carver",
      "category": 4,
      "difficulty": 2,
      "id": 12,
      "question": "Who invented Peanut Butter?"
    },
    {
      "answer": "Alexander Fleming",
      "category": 1,
      "difficulty": 3,
      "id": 21,
      "question": "Who discovered penicillin?"
    }
  ],
  "success": true,
  "total_questions": 3
}
```
Endpoint: /api/play
Functionality: Returns a random question. If a quizCategory is passed then it will return a question within that category. If previousQuestions was passed and is not empty then it will return a question whose id is not in that array of integers.
Example Request:
```JSON
{
	"quizCategory" : 3,
	"previousQuestions" : [1,2,3,4,5,6,7,8,9,10,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
}
```
Example Response:
```JSON
{
  "question": {
    "answer": "Lake Victoria",
    "category": 3,
    "difficulty": 2,
    "id": 13,
    "question": "What is the largest lake in Africa?"
  },
  "success": true
}
```


#### DELETE
Endpoint: /api/questions/<int:question_id>
Functionality: Deletes question with id of question_id from database. Returns a success boolean as well as a request object.
Example Response:
```JSON
{
  "request": {
    "answer": "1912",
    "category": 4,
    "difficulty": 3,
    "id": 35,
    "question": "What year did the Titanic Sink"
  },
  "success": true
}
```