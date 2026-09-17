import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HOST = "127.0.0.1"
PORT = 8000


USERS_DATA = {
    "user1": {
        "name": "Алексей",
        "game": "Dota 2",
        "level": 42,
        "score": 15320,
        "playtime_hours": 210,
    },
    "user2": {
        "name": "Мария",
        "game": "Valorant",
        "level": 30,
        "score": 9870,
        "playtime_hours": 95,
    },
    "user3": {
        "name": "Игорь",
        "game": "CS2",
        "level": 55,
        "score": 21000,
        "playtime_hours": 340,
    },
}


class GameStatsHandler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        body = json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")

        try:
            self.send_response(status_code)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        except (
            BrokenPipeError,
            ConnectionResetError,
            ConnectionAbortedError
        ):
            print("Клиент разорвал соединение до получения ответа.")

    def get_path_parts(self):
        return [
            part
            for part in self.path.split("?")[0].split("/")
            if part
        ]

    def do_GET(self):
        try:
            parts = self.get_path_parts()

            if parts == ["users"]:
                self.send_json(200, USERS_DATA)
                return

            if len(parts) == 2 and parts[0] == "users":
                user_id = parts[1]

                if user_id not in USERS_DATA:
                    self.send_json(
                        404,
                        {"error": "Пользователь не найден"}
                    )
                    return

                self.send_json(
                    200,
                    USERS_DATA[user_id]
                )
                return

            self.send_json(
                404,
                {"error": "Маршрут не найден"}
            )

        except Exception as error:
            print("Ошибка GET:", error)

            try:
                self.send_json(
                    500,
                    {"error": "Внутренняя ошибка сервера"}
                )
            except Exception:
                pass

    def do_POST(self):
        try:
            parts = self.get_path_parts()

            if (
                len(parts) == 3
                and parts[0] == "users"
                and parts[2] == "score"
            ):
                user_id = parts[1]

                if user_id not in USERS_DATA:
                    self.send_json(
                        404,
                        {"error": "Пользователь не найден"}
                    )
                    return

                content_length = self.headers.get("Content-Length")

                if content_length is None:
                    self.send_json(
                        400,
                        {"error": "Отсутствует тело запроса"}
                    )
                    return

                try:
                    content_length = int(content_length)
                except ValueError:
                    self.send_json(
                        400,
                        {"error": "Некорректный Content-Length"}
                    )
                    return

                if content_length <= 0:
                    self.send_json(
                        400,
                        {"error": "Отсутствует тело запроса"}
                    )
                    return

                raw_body = self.rfile.read(content_length)

                try:
                    body = json.loads(raw_body.decode("utf-8"))
                except (
                    json.JSONDecodeError,
                    UnicodeDecodeError
                ):
                    self.send_json(
                        400,
                        {"error": "Невалидный JSON"}
                    )
                    return

                if not isinstance(body, dict):
                    self.send_json(
                        400,
                        {"error": "Тело запроса должно быть JSON-объектом"}
                    )
                    return

                if "score" not in body:
                    self.send_json(
                        400,
                        {"error": "Отсутствует поле score"}
                    )
                    return

                score = body["score"]

                if isinstance(score, bool) or not isinstance(
                    score,
                    (int, float)
                ):
                    self.send_json(
                        400,
                        {"error": "Поле score должно быть числом"}
                    )
                    return

                USERS_DATA[user_id]["score"] += score

                self.send_json(
                    200,
                    USERS_DATA[user_id]
                )
                return

            if parts == ["users"]:
                self.send_json(
                    405,
                    {"error": "Метод не поддерживается"}
                )
                return

            self.send_json(
                404,
                {"error": "Маршрут не найден"}
            )

        except (
            BrokenPipeError,
            ConnectionResetError,
            ConnectionAbortedError
        ):
            print("Клиент оборвал соединение во время POST-запроса.")

        except Exception as error:
            print("Ошибка POST:", error)

            try:
                self.send_json(
                    500,
                    {"error": "Внутренняя ошибка сервера"}
                )
            except Exception:
                pass

    def do_DELETE(self):
        self.send_json(
            405,
            {"error": "Метод не поддерживается"}
        )

    def do_PUT(self):
        self.send_json(
            405,
            {"error": "Метод не поддерживается"}
        )

    def do_PATCH(self):
        self.send_json(
            405,
            {"error": "Метод не поддерживается"}
        )

    def log_message(self, format, *args):
        print(
            f"{self.client_address[0]} - "
            f"{format % args}"
        )


def main():
    server = ThreadingHTTPServer(
        (HOST, PORT),
        GameStatsHandler
    )

    print("=" * 50)
    print("Сервер игровой статистики запущен")
    print(f"Адрес: http://{HOST}:{PORT}")
    print("Для остановки нажмите Ctrl+C")
    print("=" * 50)

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nОстановка сервера...")

    finally:
        server.server_close()
        print("Сервер остановлен.")


if __name__ == "__main__":
    main()
