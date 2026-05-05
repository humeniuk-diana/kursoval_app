from db.db_connection import get_connection

class Level:
    def __init__(self, id_level, name_level, difficulty_order):
        self.id_level = id_level
        self.name_level = name_level
        self.difficulty_order = difficulty_order
#рівні беруться з бд
    @staticmethod
    def get_all_levels():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM levels ORDER BY difficulty_order")
        rows = cursor.fetchall()
        conn.close()
        return [Level(**row) for row in rows]

    def __str__(self):
        return f"{self.name_level}"
