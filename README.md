# Fix&Learn

**Empowering Developers to Learn Through Errors and Code.**

## Overview

In today’s AI-driven programming world, developers often rely on AI tools to generate or fix code efficiently. However, this reliance can sometimes skip the core understanding of the principles behind the solutions. Fix&Learn aims to bridge this gap by creating a platform where users can paste their code and errors to not only fix them but also learn the programming concepts involved.

Fix&Learn turns every error into an opportunity to grow, helping developers grasp the "why" behind the code, building confidence, and creating a stronger programming foundation.

## Features

- Paste your code and errors to get instant solutions.
- Learn the principles and core concepts behind the fixes.
- Integrates with Supabase for database operations and Together API for AI model interactions.
- Every interaction serves as a learning moment to deepen understanding.

## Technologies Used

- **Python**: Core language for backend logic.
- **FastAPI**: Framework for building the API.
- **Supabase**: Used for managing database operations.
- **Together API**: AI integration for code analysis and fixes.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Supabase account for database operations
- Together API key for AI functionality

## Setting Up Fix&Learn

### 1. Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd fix-and-learn

# Copy the environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use your preferred editor
```

### 2. Configure Environment Variables

Update your `.env` file with the following:

```plaintext
SUPABASE_URL=your-supabase-project-url
SUPABASE_SERVICE_KEY=your-supabase-service-key
TOGETHER_API_KEY=your-together-api-key
API_BEARER_TOKEN=your-bearer-token
```

### 3. Install Dependencies

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 4. Set Up the Database

Run the following SQL commands to create the required tables in Supabase:

```sql
-- Enable the pgcrypto extension for UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE messages (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT NOT NULL,
    message JSONB NOT NULL
);

CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

### 5. Start the Application

For local installation:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

For Docker installation:

```bash
# Build the Docker image
docker build -t fix-and-learn .

# Run the Docker container
docker run -d --name fix-and-learn -p 8000:8000 --env-file .env fix-and-learn
```

The application will be accessible at `http://localhost:8000`.

## Usage

1. **Submit Code and Errors:**
   Paste your code and errors via the provided API endpoint or user interface.
2. **Receive Fixes and Explanations:**
   The system provides the corrected code along with explanations of the concepts involved.
3. **Learn:**
   Review the explanations to understand the principles and strengthen your programming knowledge.

## Example Request

```bash
curl -X POST http://localhost:8000/api/fix-and-learn \
  -H "Authorization: Bearer your-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(unknown_variable)",
    "error": "NameError: name 'unknown_variable' is not defined",
    "user_id": "test-user"
  }'
```

## Example Response

```json
{
  "success": true,
  "fixed_code": "unknown_variable = 'Hello, World!'\nprint(unknown_variable)",
  "concepts": ["Variable Initialization", "Error Handling: NameError"]
}
```

## License

This project is licensed under the MIT License.

---

Build your programming skills, one error at a time, with **Fix&Learn**!

#
