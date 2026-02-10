# Planning Center API Documentation (for Postman)

## Endpoint: Get People by Birthday

**Method:** `GET` \
**URL:** `https://api.planningcenteronline.com/people/v2/people`

### 1. Authentication
*   **Type:** Basic Auth
*   **Username:** `<YOUR_PC_APP_ID>`
*   **Password:** `<YOUR_PC_SECRET>`

*(In Postman, go to the **Authorization** tab, select **Basic Auth**, and paste your credentials).*

### 2. Query Parameters
Add these keys in the **Params** tab:

| Key | Value | Description |
| :--- | :--- | :--- |
| `where[birthdate_month]` | `1` | Month integer (e.g., 1 for January) |
| `where[birthdate_day]` | `6` | Day integer (e.g., 6 for the 6th) |

**Full Example URL:**
`https://api.planningcenteronline.com/people/v2/people?where[birthdate_month]=1&where[birthdate_day]=6`

### 3. Example Response (JSON)
The API follows the JSON:API standard.
```json
{
    "data": [
        {
            "type": "Person",
            "id": "123456",
            "attributes": {
                "name": "Alex Giron",
                "first_name": "Alex",
                "last_name": "Giron",
                "birthdate": "1990-01-06",
                "anniversary": null,
                "gender": "M",
                "grade": null,
                "child": false
            },
            "links": {
                "self": "https://api.planningcenteronline.com/people/v2/people/123456"
            }
        },
        {
            "type": "Person",
            "id": "789012",
            "attributes": {
                "name": "Jane Smith",
                "first_name": "Jane",
                "last_name": "Smith",
                "birthdate": "1985-01-06"
            }
        }
    ],
    "meta": {
        "total_count": 2,
        "count": 2
    }
}
```

### 4. cURL Command (for testing)
```bash
curl -u "APP_ID:SECRET" \
  "https://api.planningcenteronline.com/people/v2/people?where[birthdate_month]=1&where[birthdate_day]=6"
```
