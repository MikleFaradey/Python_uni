import http.client
import json
import socket


HOST = "127.0.0.1"
PORT = 8000


def print_response(title, response, body):
    print("\n" + "=" * 60)
    print(title)
    print("-" * 60)
    print("HTTP status:", response.status, response.reason)

    try:
        data = json.loads(body)
        print(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            )
        )
    except json.JSONDecodeError:
        print(body)


def request(method, path, body=None):
    connection = http.client.HTTPConnection(
        HOST,
        PORT,
        timeout=5
    )

    headers = {}

    if body is not None:
        headers["Content-Type"] = "application/json"

    connection.request(
        method,
        path,
        body=body,
        headers=headers
    )

    response = connection.getresponse()
    response_body = response.read().decode("utf-8")
    connection.close()

    return response, response_body


def run_automatic_tests():
    print("=" * 60)
    print("АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ")
    print("=" * 60)

    response, body = request("GET", "/users")
    print_response("ТЕСТ 1: GET /users", response, body)

    response, body = request("GET", "/users/user2")
    print_response("ТЕСТ 2: GET /users/user2", response, body)

    response, body = request(
        "POST",
        "/users/user1/score",
        body=json.dumps({"score": 500})
    )
    print_response(
        "ТЕСТ 3: Добавление 500 очков user1",
        response,
        body
    )

    response, body = request("GET", "/users/user99")
    print_response(
        "ТЕСТ 4: Несуществующий пользователь",
        response,
        body
    )

    response, body = request("GET", "/foo")
    print_response(
        "ТЕСТ 5: Несуществующий маршрут",
        response,
        body
    )

    response, body = request(
        "POST",
        "/users/user1/score",
        body=json.dumps({"score": "abc"})
    )
    print_response(
        "ТЕСТ 6: score имеет неверный тип",
        response,
        body
    )

    response, body = request(
        "POST",
        "/users/user1/score",
        body='{"score": 100'
    )
    print_response(
        "ТЕСТ 7: Невалидный JSON",
        response,
        body
    )

    response, body = request(
        "POST",
        "/users/user1/score"
    )
    print_response(
        "ТЕСТ 8: POST без тела",
        response,
        body
    )

    response, body = request(
        "DELETE",
        "/users"
    )
    print_response(
        "ТЕСТ 9: DELETE /users",
        response,
        body
    )

    print("\n" + "=" * 60)
    print("ТЕСТ 10: Обрыв соединения во время отправки")
    print("-" * 60)

    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.connect((HOST, PORT))

        partial_request = (
            b"POST /users/user1/score HTTP/1.1\r\n"
            b"Host: 127.0.0.1\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Length: 100\r\n"
            b"\r\n"
            b'{"score":'
        )

        sock.sendall(partial_request)
        sock.close()

        print("Соединение намеренно оборвано.")
        print("Проверяем, что сервер продолжает работать.")

    except Exception as error:
        print("Ошибка при тесте обрыва:", error)

    response, body = request("GET", "/users")

    print_response(
        "КОНТРОЛЬ: сервер работает после ошибочных запросов",
        response,
        body
    )

    print("\nАвтоматические тесты завершены успешно.")


def print_help():
    print("""
Доступные примеры команд:

  GET /users
  GET /users/user1
  GET /users/user2
  GET /users/user99

  POST /users/user1/score {"score": 100}
  POST /users/user2/score {"score": -50}
  POST /users/user3/score {"score": "abc"}

  DELETE /users
  GET /foo

Служебные команды:

  help   - показать эту справку
  clear  - визуально очистить консоль
  exit   - выйти из клиента
""")


def interactive_mode():
    print("\n" + "=" * 60)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("=" * 60)
    print("Теперь можно отправлять запросы вручную.")
    print("Введите help для просмотра примеров.")
    print("Введите exit для завершения клиента.")

    while True:
        try:
            raw = input("\nrequest> ").strip()

            if not raw:
                continue

            command = raw.lower()

            if command in ("exit", "quit", "q"):
                print("Клиент завершён.")
                break

            if command == "help":
                print_help()
                continue

            if command == "clear":
                print("\n" * 40)
                continue

            parts = raw.split(maxsplit=2)

            if len(parts) < 2:
                print(
                    "Неверный формат. Используйте: "
                    "METHOD /path [JSON]"
                )
                continue

            method = parts[0].upper()
            path = parts[1]
            body = parts[2] if len(parts) == 3 else None

            if not path.startswith("/"):
                print("Маршрут должен начинаться с /")
                continue

            try:
                response, response_body = request(
                    method,
                    path,
                    body
                )

                print_response(
                    f"{method} {path}",
                    response,
                    response_body
                )

            except ConnectionRefusedError:
                print(
                    "Не удалось подключиться к серверу. "
                    "Убедитесь, что server.py запущен."
                )

            except socket.timeout:
                print("Сервер не ответил вовремя.")

            except Exception as error:
                print("Ошибка запроса:", error)

        except KeyboardInterrupt:
            print("\nКлиент завершён.")
            break

        except EOFError:
            print("\nКлиент завершён.")
            break


def main():
    try:
        run_automatic_tests()
        interactive_mode()

    except ConnectionRefusedError:
        print(
            "Не удалось подключиться к серверу.\n"
            "Сначала запустите server.py, затем client.py."
        )

    except Exception as error:
        print("Ошибка клиента:", error)


if __name__ == "__main__":
    main()
