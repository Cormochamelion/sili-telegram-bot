import sqlite3

from datetime import datetime

from sili_telegram_bot.modules.config import config

VL_CONFIG = config["voicelines"]


class ResponseDB:
    """
    Class for managing the SQLite DB for storing response & entity data.
    """

    _entity_data_columns = {
        "entity_name": "TEXT NOT NULL",
        "entity_title": "TEXT NOT NULL",
        "entity_url": "TEXT NOT NULL",
        "entity_type": "TEXT NOT NULL",
        "last_update_time": "TEXT NOT NULL",
    }

    _responses_columns = {
        "response_id": "INTEGER AUTOINCREMENT",
        "entity_title": "TEXT NOT NULL",
        "response": "TEXT NOT NULL",
        "last_update_time": "TEXT NOT NULL",
    }

    _url_columns = {
        "response_id": "INTEGER",
        "url": "TEXT NOT NULL",
        "level": "INTEGER NOT NULL",
        "last_update_time": "TEXT NOT NULL",
    }

    # TODO Ensure concurrent read & write capabilities.
    def __init__(self, db_path: str = VL_CONFIG["response_db_path"]) -> None:
        self.db_conn = sqlite3.connect(db_path)
        self.db_conn.row_factory = sqlite3.Row

        try:
            cursor = self.db_conn.cursor()
            ResponseDB._create_entity_data_table(cursor)
            ResponseDB._create_responses_table(cursor)
            ResponseDB._create_response_url_table(cursor)

            self.db_conn.commit()

        except Exception as e:
            self.db_conn.rollback()

            raise Exception(f"Error during table creation: {e}. Creation was aborted.")

    @classmethod
    def _create_table(
        cls,
        db_cursor: sqlite3.Cursor,
        table_name: str,
        column_dict: dict[str, str],
        constraints: str,
    ) -> None:
        """
        Create a SQLite table from parameters.
        """
        columns = [" ".join([key, value]) for key, value in column_dict.items()]

        command_body = ", ".join(columns + constraints)

        command = f"CREATE TABLE IF NOT EXISTS {table_name} ({command_body})"

        db_cursor.execute(command)

    @classmethod
    def _create_entity_data_table(cls, db_cursor: sqlite3.Cursor) -> None:
        """
        Create the table containing data on response entities.
        """
        table_name = "entity_data"

        constraints = ["PRIMARY KEY entity_title"]

        cls._create_table(db_cursor, table_name, cls._entity_data_columns, constraints)

    @classmethod
    def _create_responses_table(cls, db_cursor: sqlite3.Cursor) -> None:
        """
        Create the table containing each response.
        """
        table_name = "response_data"

        constraints = ["PRIMARY KEY response_id"]

        cls._create_table(db_cursor, table_name, cls._responses_columns, constraints)

    @classmethod
    def _create_response_url_table(cls, db_cursor: sqlite3.Cursor) -> None:
        """
        Create the table containing the urls for each response.
        """
        table_name = "response_urls"

        constraints = ["PRIMARY KEY url"]

        cls._create_table(db_cursor, table_name, cls._url_columns, constraints)

    def _insert_record(
        self,
        table_name: str,
        cursor: sqlite3.Cursor,
        record: dict[str, str],
        validation_dict: dict[str, str],
    ) -> None:
        """
        Insert a record into a table. The record is specified as a dict, with keys
        giving the field name. Field names are validated against the names of
        validation_dict, which is one of the column specifications of this class.
        The 'last_update_time' col is added automatically.
        """
        record["last_update_time"] = datetime.now().isoformat()
        cols = ", ".join(record.keys())

        # Ensure record names are as expected.
        if not record.keys() == validation_dict.keys:
            expected_keys = ", ".join(validation_dict.keys())
            actual_keys = ", ".join(record.keys())

            raise ValueError(
                f"Can't insert records, keys do not match. Expected: "
                f"'{expected_keys}', actual: '{actual_keys}'."
            )

        value_placeholders = ", ".join(["?" for _ in record])

        command = f"INSERT INTO {table_name} ({cols}) VALUES ({value_placeholders})"
        cursor.execute(command)

    def insert_entity_data(self, cursor: sqlite3.Cursor, **kwargs) -> str:
        self._insert_record(
            table_name="entity_data",
            cursor=cursor,
            record=kwargs,
            validation_dict=self._entity_data_columns,
        )

    def insert_response(self, cursor: sqlite3.Cursor, **kwargs) -> str:
        self._insert_record(
            table_name="response_data",
            cursor=cursor,
            record=kwargs,
            validation_dict=self._entity_data_columns,
        )

    def insert_response_url(self, cursor: sqlite3.Cursor, **kwargs) -> str:
        self._insert_record(
            table_name="response_url",
            cursor=cursor,
            record=kwargs,
            validation_dict=self._entity_data_columns,
        )


class ResponseDBWrapper:
    """
    Singleton wrapper for ResponseDB.
    """

    _response_db = None

    @classmethod
    def get_or_create_response_db(cls):
        if not cls._response_db:
            cls._response_db = ResponseDB(VL_CONFIG["response_db_path"])

        return cls._response_db
