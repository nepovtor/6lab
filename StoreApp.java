import java.sql.*;
import java.time.Year;
import java.util.Scanner;

public class StoreApp {
    private static final String DB_URL = "jdbc:sqlite:store.db";

    private static Connection connect() throws SQLException {
        return DriverManager.getConnection(DB_URL);
    }

    private static void initDb() {
        try (Connection conn = connect();
             Statement stmt = conn.createStatement()) {
            stmt.execute("CREATE TABLE IF NOT EXISTS items (" +
                    "id INTEGER PRIMARY KEY," +
                    "name TEXT NOT NULL," +
                    "price REAL NOT NULL," +
                    "quantity INTEGER NOT NULL," +
                    "release_year INTEGER NOT NULL)");
        } catch (SQLException e) {
            System.out.println("Ошибка инициализации БД: " + e.getMessage());
        }
    }

    private static int inputInt(Scanner sc, String prompt) {
        while (true) {
            System.out.print(prompt);
            String line = sc.nextLine();
            try {
                return Integer.parseInt(line);
            } catch (NumberFormatException e) {
                System.out.println("Введите целое число.");
            }
        }
    }

    private static double inputDouble(Scanner sc, String prompt) {
        while (true) {
            System.out.print(prompt);
            String line = sc.nextLine();
            try {
                return Double.parseDouble(line);
            } catch (NumberFormatException e) {
                System.out.println("Введите число.");
            }
        }
    }

    private static int inputYear(Scanner sc, String prompt) {
        int current = Year.now().getValue();
        while (true) {
            int year = inputInt(sc, prompt);
            if (year >= 1900 && year <= current) {
                return year;
            }
            System.out.println("Введите корректный год (от 1900 до " + current + ")");
        }
    }

    private static void addItem(Scanner sc) {
        try (Connection conn = connect()) {
            PreparedStatement checkStmt = conn.prepareStatement("SELECT id FROM items WHERE id=?");
            int id = inputInt(sc, "ID товара: ");
            checkStmt.setInt(1, id);
            if (checkStmt.executeQuery().next()) {
                System.out.println("Товар с таким ID уже существует.");
                return;
            }
            System.out.print("Название: ");
            String name = sc.nextLine();
            double price = inputDouble(sc, "Стоимость: ");
            int quantity = inputInt(sc, "Количество: ");
            int releaseYear = inputYear(sc, "Год выпуска: ");
            PreparedStatement ins = conn.prepareStatement(
                    "INSERT INTO items(id, name, price, quantity, release_year) VALUES (?, ?, ?, ?, ?)");
            ins.setInt(1, id);
            ins.setString(2, name);
            ins.setDouble(3, price);
            ins.setInt(4, quantity);
            ins.setInt(5, releaseYear);
            ins.executeUpdate();
            System.out.println("Товар добавлен.");
        } catch (SQLException e) {
            System.out.println("Ошибка добавления: " + e.getMessage());
        }
    }

    private static void listItems() {
        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT * FROM items")) {
            while (rs.next()) {
                System.out.printf("%d %s %.2f %d %d\n",
                        rs.getInt("id"),
                        rs.getString("name"),
                        rs.getDouble("price"),
                        rs.getInt("quantity"),
                        rs.getInt("release_year"));
            }
        } catch (SQLException e) {
            System.out.println("Ошибка чтения: " + e.getMessage());
        }
    }

    private static void deleteItem(Scanner sc) {
        int id = inputInt(sc, "ID товара для удаления: ");
        try (Connection conn = connect();
             PreparedStatement stmt = conn.prepareStatement("DELETE FROM items WHERE id=?")) {
            stmt.setInt(1, id);
            int rows = stmt.executeUpdate();
            if (rows == 0) {
                System.out.println("Товар не найден.");
            } else {
                System.out.println("Товар удален.");
            }
        } catch (SQLException e) {
            System.out.println("Ошибка удаления: " + e.getMessage());
        }
    }

    private static void updateItem(Scanner sc) {
        int id = inputInt(sc, "ID товара для обновления: ");
        try (Connection conn = connect()) {
            PreparedStatement check = conn.prepareStatement("SELECT * FROM items WHERE id=?");
            check.setInt(1, id);
            ResultSet rs = check.executeQuery();
            if (!rs.next()) {
                System.out.println("Товар не найден.");
                return;
            }
            System.out.print("Новое название: ");
            String name = sc.nextLine();
            double price = inputDouble(sc, "Новая стоимость: ");
            int quantity = inputInt(sc, "Новое количество: ");
            int releaseYear = inputYear(sc, "Новый год выпуска: ");
            PreparedStatement upd = conn.prepareStatement(
                    "UPDATE items SET name=?, price=?, quantity=?, release_year=? WHERE id=?");
            upd.setString(1, name);
            upd.setDouble(2, price);
            upd.setInt(3, quantity);
            upd.setInt(4, releaseYear);
            upd.setInt(5, id);
            upd.executeUpdate();
            System.out.println("Товар обновлен.");
        } catch (SQLException e) {
            System.out.println("Ошибка обновления: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        initDb();
        Scanner sc = new Scanner(System.in);
        while (true) {
            System.out.println("1. Добавить товар");
            System.out.println("2. Показать все");
            System.out.println("3. Удалить товар");
            System.out.println("4. Обновить товар");
            System.out.println("0. Выход");
            System.out.print("Выберите действие: ");
            String choice = sc.nextLine();
            switch (choice) {
                case "1":
                    addItem(sc);
                    break;
                case "2":
                    listItems();
                    break;
                case "3":
                    deleteItem(sc);
                    break;
                case "4":
                    updateItem(sc);
                    break;
                case "0":
                    sc.close();
                    return;
                default:
                    System.out.println("Неверный выбор.");
            }
        }
    }
}
