import psycopg2
import logging
from groq import Groq
from sentence_transformers import SentenceTransformer
from config.settings import DATABASE_URL, GROQ_API_KEY, EMBEDDING_MODEL_NAME

# Embedding model ko ek baar load karte hain
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Groq client ko ek baar create karte hain
groq_client = Groq(api_key=GROQ_API_KEY)


def connect_to_db():
    # PostgreSQL database se connection banate hain
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def semantic_search(conn, query, state=None, top_k=5):

    # User query ko vector mein convert karte hain
    query_embedding = model.encode(query).tolist()

    cursor = conn.cursor()

    # Agar state diya hai to sirf us state ke colleges search karenge
    if state:
        sql = """
            SELECT name,
                   state,
                   district,
                   college_type,
                   management,
                   university_name,
                   reference_search_url
            FROM colleges
            WHERE state = %s
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """

        cursor.execute(sql,(state, query_embedding, top_k))

    # Agar state nahi diya hai to poore database mein search karenge
    else:
        sql = """
            SELECT name,
                   state,
                   district,
                   college_type,
                   management,
                   university_name,
                   reference_search_url
            FROM colleges
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """

        cursor.execute(
            sql,
            (query_embedding, top_k)
        )

    colleges = cursor.fetchall()

    cursor.close()

    logging.info(
        f"Semantic search returned {len(colleges)} colleges"
    )

    return colleges


def generate_recommendation(colleges, query):

    # Colleges ko text format mein convert karte hain
    colleges_text = "\n".join([
        f"- {college[0]}, {college[2]}, {college[1]} "
        f"({college[3]}, {college[4]}), "
        f"Affiliated to {college[5]}, "
        f"More info: {college[6]}"
        for college in colleges
    ])

    # LLM ko user query aur matching colleges dete hain
    prompt = f"""
    A student asked: "{query}"

    Here are matching colleges:
    {colleges_text}

    Recommend the top 3 colleges from this list.
    Write the entire response in clear, professional English only.
    Keep it brief and clear.

    DATA LIMITATION:
    You only have this data about each college:
    name, location, type, management, and university affiliation.

    You do NOT have fees, placement records, rankings,
    or quality/infrastructure ratings.

    NEVER state or imply anything about fees being
    "low", "high", or "budget-friendly".

    NEVER state or imply anything about placements being
    "good", "strong", or "solid".

    If the student's question involves fees, placement,
    or rankings, clearly say that you do not have that data
    and share the "More info" link so they can check themselves.
    """

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def get_recommendations(query, state=None):
    conn = connect_to_db()
    colleges = semantic_search(conn, query, state=state, top_k=5)
    conn.close()
    # Agar koi college nahi mila to message return karte hain
    if not colleges:
        return "No matching colleges found. Try changing the filters."

    # Matching colleges ko LLM ke paas bhejkar recommendation banate hain
    recommendation = generate_recommendation(colleges, query)
    return recommendation

if __name__ == "__main__":

    # Test query
    query = "budget engineering college with good placement"

    # State filter
    state = "Delhi"

    # Recommendation generate karte hain
    result = get_recommendations(query, state=state)

    # Final recommendation print karte hain
    print(result)