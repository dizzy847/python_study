# set убирает повторяющиеся множества
# frozenset замораживает список и его никак нельзя изменить

# ФУНКЦИИ
# def test_func():
#     print('Hello', end="")
#     print("!")
#
# test_func()

# def test_func(word):
#     print(word, end="")
#     print("!")
#
# test_func("Hi")
# test_func(5)
# test_func(6.5)

# def summa(a, b):
#     res = a + b
#     print("Result:", res)
#
# summa(5, 7)
# summa("H", "I")

# def summa(a, b):
#     return a + b
#
# res = summa(5, 7)
# print(res)

def minimal(l):
    min_number = l[0]
    for i in l:
        if i < min_number:
            min_number = i
    print(min_number)

nums_1 = [5, 7, 2, 9, 4]
minimal(nums_1)

nums_2 = [5.4, 7.2, 2.3, 2.1, 9.4, 4.2]
minimal(nums_2)

# func = lambda x, y: x * y
# res = func(5, 2)
# print(res) результат 10


package com.javatest;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;

public class Main extends JFrame {

    // Структура данных для хранения вопроса
    static class Question {
        String text; String[] options; int correctIndex;
        public Question(String text, String[] options, int correctIndex) {
            this.text = text; this.options = options; this.correctIndex = correctIndex;
        }
    }

    // Банк из 5 вопросов по Java
    private final Question[] questions = {
        new Question("Что выведет данный фрагмент кода на экран?\n\nint a = 10;\nint b = 3;\nSystem.out.println(a % b);", new String[]{"3", "1", "3.33", "Ошибка компиляции"}, 1),
        new Question("Какой метод является стандартной точкой входа (запуска) в Java-приложении?", new String[]{"start()", "init()", "main()", "run()"}, 2),
        new Question("Какое ключевое слово используется для наследования классов в Java?", new String[]{"implements", "inherits", "extends", "this"}, 2),
        new Question("Какой тип данных используется в Java для хранения целых чисел по умолчанию?", new String[]{"int", "long", "byte", "short"}, 0),
        new Question("Что из перечисленного НЕ является базовым принципом объектно-ориентированного программирования (ООП)?", new String[]{"Инкапсуляция", "Полиморфизм", "Компиляция", "Наследование"}, 2)
    };

    private int currentIndex = 0, correctAnswersCount = 0;
    private JPanel mainPanel;
    private JLabel lblProgress;
    private JTextArea txtQuestionArea;
    private final JRadioButton[] radioButtons = new JRadioButton[4];
    private final ButtonGroup buttonGroup = new ButtonGroup();
    private JButton btnNext;

    // Константы фирменной палитры Space Dark
    private final Color bgDark = new Color(30, 35, 45), bgCode = new Color(20, 24, 33);
    private final Color cMint = new Color(166, 226, 46), cBlue = new Color(52, 152, 219);

    public Main() {
        setTitle("Система автоматизированного контроля знаний студентов");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(900, 650);
        setLocationRelativeTo(null);
        setResizable(true); // Разрешаем разворачивать окно

        mainPanel = new JPanel(new GridBagLayout());
        mainPanel.setBackground(bgDark);
        mainPanel.setBorder(new EmptyBorder(25, 25, 25, 25));
        add(mainPanel);

        // Инициализируем Главное меню вместо мгновенного старта теста
        showMainMenu(); 
    }

    // Метод отрисовки Главного меню
    private void showMainMenu() {
        mainPanel.removeAll();
        mainPanel.setLayout(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.CENTER;

        // Заголовок
        JLabel lblMainTitle = new JLabel("АВТОМАТИЗИРОВАННАЯ СИСТЕМА", SwingConstants.CENTER);
        lblMainTitle.setFont(new Font("Segoe UI", Font.BOLD, 32));
        lblMainTitle.setForeground(cMint);
        gbc.gridy = 0;
        gbc.insets = new Insets(0, 0, 10, 0);
        mainPanel.add(lblMainTitle, gbc);

        // Подзаголовок
        JLabel lblSubTitle = new JLabel("КОНТРОЛЯ ЗНАНИЙ ПО JAVA", SwingConstants.CENTER);
        lblSubTitle.setFont(new Font("Segoe UI", Font.BOLD, 28));
        lblSubTitle.setForeground(Color.WHITE);
        gbc.gridy = 1;
        gbc.insets = new Insets(0, 0, 60, 0);
        mainPanel.add(lblSubTitle, gbc);

        // Кнопка начала тестирования
        JButton btnStart = new JButton("Начать тестирование");
        btnStart.setBackground(cBlue);
        btnStart.setForeground(Color.WHITE);
        btnStart.setFont(new Font("Segoe UI", Font.BOLD, 18));
        btnStart.setFocusPainted(false);
        btnStart.setBorderPainted(false);
        btnStart.setPreferredSize(new Dimension(280, 50));
        btnStart.addActionListener(e -> startQuiz()); // Запускаем тест по клику
        gbc.gridy = 2;
        gbc.insets = new Insets(0, 0, 20, 0);
        mainPanel.add(btnStart, gbc);

        // Кнопка выхода из программы
        JButton btnExit = new JButton("Выход");
        btnExit.setBackground(bgCode);
        btnExit.setForeground(Color.WHITE);
        btnExit.setFont(new Font("Segoe UI", Font.BOLD, 16));
        btnExit.setFocusPainted(false);
        btnExit.setBorderPainted(false);
        btnExit.setPreferredSize(new Dimension(280, 45));
        btnExit.addActionListener(e -> System.exit(0));
        gbc.gridy = 3;
        gbc.insets = new Insets(0, 0, 0, 0);
        mainPanel.add(btnExit, gbc);

        mainPanel.revalidate();
        mainPanel.repaint();
    }

    // Метод (пере)запускает тест, обнуляет счетчики и строит разметку заново
    private void startQuiz() {
        currentIndex = 0; correctAnswersCount = 0;
        mainPanel.removeAll();
        mainPanel.setLayout(new GridBagLayout());

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0;
        
        // 1. Строка прогресса
        lblProgress = new JLabel();
        lblProgress.setFont(new Font("Segoe UI", Font.BOLD, 15));
        lblProgress.setForeground(cMint);
        
        gbc.gridy = 0;
        gbc.weightx = 1.0;
        gbc.weighty = 0.0;
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(0, 0, 15, 0);
        mainPanel.add(lblProgress, gbc);

        // 2. Текстовое поле вопроса
        txtQuestionArea = new JTextArea();
        txtQuestionArea.setEditable(false);
        txtQuestionArea.setBackground(bgCode);
        txtQuestionArea.setForeground(new Color(248, 248, 242));
        txtQuestionArea.setFont(new Font("Consolas", Font.PLAIN, 16));
        txtQuestionArea.setLineWrap(true); txtQuestionArea.setWrapStyleWord(true);
        txtQuestionArea.setMargin(new Insets(20, 20, 20, 20));

        JScrollPane scrollPane = new JScrollPane(txtQuestionArea);
        scrollPane.setBorder(BorderFactory.createLineBorder(new Color(75, 85, 105), 3)); // Жирная стильная рамка
        
        gbc.gridy = 1; 
        gbc.weighty = 1.0; // Забирает всё свободное вертикальное пространство
        gbc.fill = GridBagConstraints.BOTH; // Растягивается во все стороны
        gbc.insets = new Insets(0, 0, 15, 0);
        mainPanel.add(scrollPane, gbc);

        // 3. Панель вариантов ответов
        JPanel optionsPanel = new JPanel(new GridLayout(4, 1, 0, 10));
        optionsPanel.setBackground(bgDark);
        for (int i = 0; i < 4; i++) {
            radioButtons[i] = new JRadioButton();
            radioButtons[i].setFont(new Font("Segoe UI", Font.PLAIN, 15));
            radioButtons[i].setForeground(Color.WHITE);
            radioButtons[i].setBackground(bgDark);
            radioButtons[i].setFocusPainted(false);
            buttonGroup.add(radioButtons[i]);
            optionsPanel.add(radioButtons[i]);
        }
        
        gbc.gridy = 2; 
        gbc.weighty = 0.0; // Не растягивается по вертикали больше нужного
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(5, 5, 15, 0);
        mainPanel.add(optionsPanel, gbc);

        // 4. Кнопка "Далее"
        btnNext = new JButton("Далее →");
        btnNext.setBackground(cBlue); btnNext.setForeground(Color.WHITE);
        btnNext.setFont(new Font("Segoe UI", Font.BOLD, 15));
        btnNext.setFocusPainted(false); btnNext.setBorderPainted(false);
        btnNext.setPreferredSize(new Dimension(140, 40));
        btnNext.addActionListener(e -> checkAnswerAndProceed());

        gbc.gridy = 3; 
        gbc.weighty = 0.0;
        gbc.fill = GridBagConstraints.NONE; 
        gbc.anchor = GridBagConstraints.LINE_END; // Строго к правому краю
        gbc.insets = new Insets(10, 0, 0, 0);
        mainPanel.add(btnNext, gbc);

        displayQuestion();
        mainPanel.revalidate(); mainPanel.repaint();
    }

    private void displayQuestion() {
        if (currentIndex < questions.length) {
            Question q = questions[currentIndex];
            lblProgress.setText(" РЕЖИМ ТЕСТИРОВАНИЯ • Вопрос " + (currentIndex + 1) + " из " + questions.length);
            txtQuestionArea.setText(q.text);
            for (int i = 0; i < 4; i++) radioButtons[i].setText(q.options[i]);
            buttonGroup.clearSelection();
        } else {
            showResults();
        }
    }

    private void checkAnswerAndProceed() {
        int selectedIndex = -1;
        for (int i = 0; i < 4; i++) {
            if (radioButtons[i].isSelected()) { selectedIndex = i; break; }
        }

        if (selectedIndex == -1) {
            // Вызов нового стилизованного окна
            showCustomWarning("Внимание! Необходимо выбрать один из вариантов ответа.");
            return;
        }

        if (selectedIndex == questions[currentIndex].correctIndex) correctAnswersCount++;
        currentIndex++;
        displayQuestion();
    }

    // Кастомный метод для красивого вывода предупреждения
    private void showCustomWarning(String message) {
        JDialog dialog = new JDialog(this, "Предупреждение", true);
        dialog.setResizable(false);

        JPanel panel = new JPanel(new GridBagLayout());
        panel.setBackground(bgDark);
        panel.setBorder(new EmptyBorder(25, 30, 25, 30));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0;
        
        // Текст сообщения
        JLabel lblMessage = new JLabel(message, SwingConstants.CENTER);
        lblMessage.setFont(new Font("Segoe UI", Font.PLAIN, 15));
        lblMessage.setForeground(Color.WHITE);
        gbc.gridy = 0;
        gbc.insets = new Insets(0, 0, 20, 0);
        panel.add(lblMessage, gbc);

        // Стильная кнопка ОК
        JButton btnOk = new JButton("OK");
        btnOk.setBackground(cBlue);
        btnOk.setForeground(Color.WHITE);
        btnOk.setFont(new Font("Segoe UI", Font.BOLD, 14));
        btnOk.setFocusPainted(false);
        btnOk.setBorderPainted(false);
        btnOk.setPreferredSize(new Dimension(100, 35));
        btnOk.addActionListener(e -> dialog.dispose());
        
        gbc.gridy = 1;
        gbc.insets = new Insets(0, 0, 0, 0);
        gbc.anchor = GridBagConstraints.CENTER;
        panel.add(btnOk, gbc);

        dialog.add(panel);
        dialog.pack();
        dialog.setLocationRelativeTo(this); // Центрирование относительно главного окна
        dialog.setVisible(true);
    }

    private void showResults() {
        mainPanel.removeAll();
        mainPanel.setLayout(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0; gbc.fill = GridBagConstraints.HORIZONTAL; gbc.anchor = GridBagConstraints.CENTER;

        int percent = (correctAnswersCount * 100) / questions.length;
        int grade = (percent >= 90) ? 5 : (percent >= 75) ? 4 : (percent >= 50) ? 3 : 2;
        
        Color gradeColor = (grade == 5) ? cMint : (grade == 4) ? cBlue : 
                           (grade == 3) ? new Color(241, 196, 15) : new Color(231, 76, 60);

        JLabel lblTitle = new JLabel("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО", SwingConstants.CENTER);
        lblTitle.setFont(new Font("Segoe UI", Font.BOLD, 24)); lblTitle.setForeground(Color.WHITE);
        gbc.gridy = 0; gbc.insets = new Insets(0, 0, 30, 0); mainPanel.add(lblTitle, gbc);

        JLabel lblGrade = new JLabel("ВАША ОЦЕНКА: " + grade, SwingConstants.CENTER);
        lblGrade.setFont(new Font("Segoe UI", Font.BOLD, 36)); lblGrade.setForeground(gradeColor);
        gbc.gridy = 1; gbc.insets = new Insets(0, 0, 25, 0); mainPanel.add(lblGrade, gbc);

        String statsText = String.format(
            "<html><div style='text-align: center; font-family: Segoe UI; font-size: 14pt; color: #BDC3C7; line-height: 1.7;'>"
            + "Правильных ответов: <b style='color: white;'>%d</b> из <b>%d</b><br>"
            + "Процент успешности: <b style='color: white;'>%d%%</b><br>"
            + "Статус: <b style='color: %s;'>%s</b>"
            + "</div></html>",
            correctAnswersCount, questions.length, percent,
            (grade >= 3 ? "#A6E22E" : "#E74C3C"), (grade >= 3 ? "Тест успешно сдан" : "Требуется пересдача")
        );
        JLabel lblStats = new JLabel(statsText, SwingConstants.CENTER);
        gbc.gridy = 2; gbc.insets = new Insets(0, 0, 35, 0); mainPanel.add(lblStats, gbc);

        // Панель для кнопок в ряд на экране результатов
        JPanel btnPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 0));
        btnPanel.setBackground(bgDark);

        // КНОПКА ПЕРЕПРОХОЖДЕНИЯ ТЕСТА (теперь ведет на Главное меню)
        JButton btnRestart = new JButton("На главную");
        btnRestart.setBackground(cMint); btnRestart.setForeground(bgDark);
        btnRestart.setFont(new Font("Segoe UI", Font.BOLD, 15));
        btnRestart.setFocusPainted(false); btnRestart.setBorderPainted(false);
        btnRestart.setPreferredSize(new Dimension(180, 45));
        btnRestart.addActionListener(e -> showMainMenu()); 
        btnPanel.add(btnRestart);

        JButton btnExit = new JButton("Выход из системы");
        btnExit.setBackground(cBlue); btnExit.setForeground(Color.WHITE);
        btnExit.setFont(new Font("Segoe UI", Font.BOLD, 15));
        btnExit.setFocusPainted(false); btnExit.setBorderPainted(false);
        btnExit.setPreferredSize(new Dimension(180, 45));
        btnExit.addActionListener(e -> System.exit(0));
        btnPanel.add(btnExit);

        gbc.gridy = 3; gbc.fill = GridBagConstraints.NONE; mainPanel.add(btnPanel, gbc);

        mainPanel.revalidate(); mainPanel.repaint();
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new Main().setVisible(true));
    }
}
