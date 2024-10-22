# Анализ данных фитнес-клуба

---

Библиотеки:

**`pandas`**  **`sklearn`**  **`matplotlib`**  **`seaborn`**

---

Сеть фитнес-центров разрабатывает стратегию взаимодействия с пользователями на основе аналитических данных. Необходимо провести исследовательский анализ данных и спрогнозировать вероятность оттока на уровне следующего месяца для каждого клиента

### Описание данных

Данные на месяц до оттока и факт оттока на определённый месяц. Набор данных включает следующие поля:

- `'Churn'` — факт оттока в текущем месяце;
- Текущие поля в датасете:
    - Данные пользователя за предыдущий до проверки факта оттока месяц:
        - `'gender'` — пол
        - `'Near_Location'` — проживание или работа в районе, где находится фитнес-центр
        - `'Partner'` — сотрудник компании-партнёра клуба (сотрудничество с компаниями, чьи сотрудники могут получать скидки на абонемент — в таком случае фитнес-центр хранит информацию о работодателе клиента)
        - `Promo_friends` — факт первоначальной записи в рамках акции «приведи друга» (использовал промо-код от знакомого при оплате первого абонемента)
        - `'Phone'` — наличие контактного телефона
        - `'Age'` — возраст
        - `'Lifetime'` — время с момента первого обращения в фитнес-центр (в месяцах)
- Информация на основе журнала посещений, покупок и информация о текущем статусе абонемента клиента
    - `'Contract_period'` — длительность текущего действующего абонемента (месяц, 3 месяца, 6 месяцев, год)
    - `'Month_to_end_contract'` — срок до окончания текущего действующего абонемента (в месяцах)
    - `'Group_visits'` — факт посещения групповых занятий
    - `'Avg_class_frequency_total'` — средняя частота посещений в неделю за все время с начала действия абонемента
    - `'Avg_class_frequency_current_month'` — средняя частота посещений в неделю за предыдущий месяц
    - `'Avg_additional_charges_total'` — суммарная выручка от других услуг фитнес-центра: кафе, спорт-товары, косметический и массажный салон

### Краткое описание проделанной работы и полученных результатов

В данном проекте использовано машинное обучение. Спрогнозирована вероятность оттока (на уровне следующего месяца) для каждого клиента; сформированы типичные портреты пользователей: выделены наиболее яркие группы, охарактеризованы их основные свойства; проанализированы основные признаки, наиболее сильно влияющие на отток.

По итогам исследования выделены 3 группы пользователей - младше 25 лет, 25-30 лет и старше 30 лет

Рекомендовал задуматься над удержанием аудитории 25 лет и младше. Возможно, отток связан с высокой ценой абонемента

Стоит сосредоточиться на увеличении количества клиентов из наиболее лояльной группы - 30 и старше. Так как основной доход (от длительных контрактов и больших трат на сопутствующие услуги) приносят они.

Предложил вести обзвон клиентов либо каким-то другими способами напоминать ему о том, что он давно не ходил в клуб - так у клиента будет вырабатываться привычка к посещению и он будет продлевать свой абонемент дальше.
