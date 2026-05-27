--
-- PostgreSQL database dump
--

\restrict EP4bTFloX1W07i3XnCccVxDCK2WMBaSdz3V9pPyGm87ZpPBPibO9xeLGsHFJ0C1

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: event_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_plans (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    event_date date NOT NULL,
    event_time time without time zone,
    location character varying(255),
    description text,
    speaker character varying(255),
    audience character varying(100),
    created_by integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    event_end_time time without time zone,
    category character varying(100)
);


ALTER TABLE public.event_plans OWNER TO postgres;

--
-- Name: COLUMN event_plans.category; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.event_plans.category IS 'Категория мероприятия (конференция, семинар и т.д.)';


--
-- Name: event_plans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.event_plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_plans_id_seq OWNER TO postgres;

--
-- Name: event_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.event_plans_id_seq OWNED BY public.event_plans.id;


--
-- Name: file_access_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.file_access_log (
    id integer NOT NULL,
    user_id integer,
    operation character varying(50),
    file_path character varying(500),
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.file_access_log OWNER TO postgres;

--
-- Name: file_access_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.file_access_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.file_access_log_id_seq OWNER TO postgres;

--
-- Name: file_access_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.file_access_log_id_seq OWNED BY public.file_access_log.id;


--
-- Name: generated_news; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.generated_news (
    id integer NOT NULL,
    event_plan_id integer,
    generated_text text NOT NULL,
    generation_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_approved boolean DEFAULT false,
    approved_by integer,
    rating integer,
    user_id integer,
    CONSTRAINT generated_news_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE public.generated_news OWNER TO postgres;

--
-- Name: COLUMN generated_news.user_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.generated_news.user_id IS 'Пользователь, который сгенерировал новость';


--
-- Name: generated_news_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.generated_news_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.generated_news_id_seq OWNER TO postgres;

--
-- Name: generated_news_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.generated_news_id_seq OWNED BY public.generated_news.id;


--
-- Name: generation_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.generation_logs (
    id integer NOT NULL,
    event_plan_id integer,
    user_id integer,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    prompt_text text,
    generated_text text,
    success boolean,
    error_message text,
    inference_time_ms integer
);


ALTER TABLE public.generation_logs OWNER TO postgres;

--
-- Name: generation_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.generation_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.generation_logs_id_seq OWNER TO postgres;

--
-- Name: generation_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.generation_logs_id_seq OWNED BY public.generation_logs.id;


--
-- Name: reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reports (
    id integer NOT NULL,
    report_type character varying(50),
    file_path character varying(500),
    generated_by integer,
    generated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    parameters jsonb
);


ALTER TABLE public.reports OWNER TO postgres;

--
-- Name: reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reports_id_seq OWNER TO postgres;

--
-- Name: reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reports_id_seq OWNED BY public.reports.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.settings (
    id integer NOT NULL,
    setting_key character varying(100) NOT NULL,
    setting_value text,
    description text,
    updated_by integer,
    updated_at timestamp without time zone
);


ALTER TABLE public.settings OWNER TO postgres;

--
-- Name: settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.settings_id_seq OWNER TO postgres;

--
-- Name: settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.settings_id_seq OWNED BY public.settings.id;


--
-- Name: templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.templates (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    template_text text NOT NULL,
    description text,
    is_default boolean DEFAULT false
);


ALTER TABLE public.templates OWNER TO postgres;

--
-- Name: templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.templates_id_seq OWNER TO postgres;

--
-- Name: templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.templates_id_seq OWNED BY public.templates.id;


--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_sessions (
    id integer NOT NULL,
    user_id integer,
    session_token character varying(255) NOT NULL,
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_sessions OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_sessions_id_seq OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_sessions_id_seq OWNED BY public.user_sessions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    email character varying(100) NOT NULL,
    role_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_login timestamp without time zone,
    is_active boolean DEFAULT true
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: event_plans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_plans ALTER COLUMN id SET DEFAULT nextval('public.event_plans_id_seq'::regclass);


--
-- Name: file_access_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_access_log ALTER COLUMN id SET DEFAULT nextval('public.file_access_log_id_seq'::regclass);


--
-- Name: generated_news id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generated_news ALTER COLUMN id SET DEFAULT nextval('public.generated_news_id_seq'::regclass);


--
-- Name: generation_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generation_logs ALTER COLUMN id SET DEFAULT nextval('public.generation_logs_id_seq'::regclass);


--
-- Name: reports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports ALTER COLUMN id SET DEFAULT nextval('public.reports_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.settings ALTER COLUMN id SET DEFAULT nextval('public.settings_id_seq'::regclass);


--
-- Name: templates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.templates ALTER COLUMN id SET DEFAULT nextval('public.templates_id_seq'::regclass);


--
-- Name: user_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN id SET DEFAULT nextval('public.user_sessions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: event_plans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_plans (id, title, event_date, event_time, location, description, speaker, audience, created_by, created_at, updated_at, event_end_time, category) FROM stdin;
7	Ргг	2026-05-12	23:15:00	Стрименговая площадка	Стример тиджой крутит гамбу	Тидж	Общение	1	2026-05-11 03:40:02.73665	\N	\N	\N
6	Мероприятие в торговомс центре Галерея!	2026-05-11	15:30:00	Город Видное, Лененский округ, Тц Галерея	Будет выступление музыкальной группы Login-Horizont в честь праздника к Дню победы 9 мая	Антонио Б.Н, Клейн М.Р, Бенсон К.Н	Сцена	1	2026-05-11 01:46:47.974776	2026-05-11 23:07:31.153866	\N	\N
8	Презентация нового Робота	2026-05-15	00:00:00	Москва, Повельён	Робот AZ900-MC созданый для поднятия и перемещения тежолых предметов	\N	Конференция	1	2026-05-15 15:09:17.14551	\N	\N	\N
9	Ярмарка на Красной площади	2026-01-22	10:00:00	Москва, Красная площадь	Ярмарка проводиться в честь китайского нового года, у будет проходить с 21 января до конца февраля.	\N	\N	1	2026-05-16 13:50:57.132359	\N	\N	\N
30	Тест	2026-05-26	\N	Майкоп	Что то будет	\N	\N	6	2026-05-26 18:40:05.37103	\N	\N	Воркшоп
16	Научная конференция	2026-05-29	09:00:00	Сковородино	Что то будет	\N	Ученые	2	2026-05-23 20:52:25.380996	2026-05-26 19:37:13.839353	21:00:00	Воркшоп
32	ergeg	2026-05-27	01:00:00	eg	ergrth	\N	\N	2	2026-05-27 07:16:36.875671	2026-05-27 07:16:44.631328	22:58:00	egrjtj
\.


--
-- Data for Name: file_access_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.file_access_log (id, user_id, operation, file_path, "timestamp") FROM stdin;
\.


--
-- Data for Name: generated_news; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.generated_news (id, event_plan_id, generated_text, generation_date, is_approved, approved_by, rating, user_id) FROM stdin;
24	7	В Тандеме стартовал стриминговый марафон. Участники генерируют новости за 24 часа и получают призы — подписку на RGB-канал для своих проектов в интернете (доступно только зарегистрированным пользователям). Дата, время проведения 2026 год; продолжительность 1 час 30 минут с перерывом между раундами 10 часов 15 мин./30 сек.; приз 500 000 руб., приглашение от организаторов к участию через мессенджер Telegram + GitHub+1/2. Спикеры из разных городов России разыграли гранты до 300 тыс рублей каждому участнику! Призовой фонд 100 тысяч долларов США уже получен командой проекта «Твиттер». Следите вместе со мной ☎ 8(916)512–06‑07−24 или пишите мне twitter@twitpicasafterslotbox . Аудитория канала более 2 млн человек ежедневно подписываются друг другу лайками. Новостной поток разослали всем участникам прямо во френдленте без спама. Лучшие посты попадут прямиком генератору контента Tweeter™. Победители получат приглашения посетить конференцию MLM 2020 года бесплатно. Подключайтесь сейчас же после регистрации у нас онлайн — https://githube.com/. Регистрация открыта круглосуточно. Время старта 19 ч 45 м мск. Место сбора Москва, ВДНХ павильон №75. Описание мероприятия можно посмотреть здесь http://www.runcitymassage2016.ru/events_newsletter?from=nodejournal&amp;&nbsp;. Запускаем хакатон #TelegramCallbackSecondary#НовостиВокругМира2027. Запись доступна также там. Ждём заявок участников 27 мая 2018 г.: подробности тут https://telegrammeoutfitterschool21startup2018.org/20180628-0111008777. Количество мест ограничено количеством подписчиков команды. Заявки принимаются как анонимные так и открытые аккаунтами соцсетей. Стартовал конкурс прогнозов погоды Pandora Lab 2019. Лучшее предсказание обойдётся организаторам минимум $100000 плюс публикация статьи об этом событии. Даны	2026-05-25 16:28:56.85396	f	2	\N	1
33	7	В Тандеме прошёл стриминг-хакатон. Участники генерируют заголовки и постскриптумы к ним за 24 часа с помощью GitHub, а приз — подписка на Runway для Android (50 000 руб.). Приз от Google Play + публикация в журнале «Киберспорт». Дата проведения 2026 год; время 19 часов 10 минут вечера. Спикеры из России разыграли поездку до Москвы без пересадок через Москву Uber или билет домой со скидкой 50%. Победители получат приглашение посетить конференцию Mobius 2016 уже завтра! А также гранты 500 тыс рублей каждый месяц как минимум разово при поддержке Фонда Потанина. Лучшие статьи попадут во все журналы мира плюс стажировки у лучших тренеров страны. Заявки принимаются здесь же после регистрации участников. Стартовал хакутин года 2018/2019 под названием Python StripDay 2+1. Время 18 ч 30 мин утра мск./16 июня 2019 г.; место сбора Москва, ITMC РАН. Описание мероприятия тут . Регистрация открыта всем желающим вне зависимости пол не важен уровень владения языком программирования. Вход свободный. Новостей много (@thedailybeast). Запущен канал YouTube https://www2.youtube.com/. Следите вместе c нами ★️♥📌Запись доступна только подписчикам канала TEDxPoons. Подключайтесь прямо сейчас 😉#studenthack2018 #TedXProjects pic.twitter.com/ZKGLvUfSuVgI&mdash;&nbsp;&#39;.Тренировка №3 (видео)В субботу стартовал онлайн курс обучения навыкам стримминга. Запись можно посмотреть ЗДЕСЬ. Расписание занятий см.: http://telegrammeoutletworkshop.ru/events_andresenko__2017?utl=trueВремя работы 11–00—18−30. Место встречи Новосибирск Академгородк Технопарк Онлайн. Зарегистрироваться нужно заблаговременно 8 мая 2020. Количество мест ограничено 100 человек. Предварительная запись обязательна!!! Ждём вас 9 апреля вечером возле метро Октябрьская кольце	2026-05-26 03:17:29.256026	f	2	\N	1
36	30	В Майкопе стартовал хакатон «Мозговой штурм». Командам предстоит написать текст на тему когнитивных искажений. Приз — подписка и стажировка в Google Discord! Дата проведения 2026-07-20, время 19 часов (время московское). Спикеры из Москвы расскажут об алгоритмах нейросетей для распознавания образов с точностью до 10%. Лучшие команды получат гранты от фонда Потанина за счёт спонсоров проекта. Новостью поделилась директор департамента образования Светлана Соколова : участники протестируют свои навыки через Python 3DMarketing + GitHub 2K/3GPL+Javascript к концу недели результаты будут опубликованы во всех школах региона. Победители попадут бесплатно домой тестировать новые приложения уже сейчас. Поддержку проекту оказывает фонд Сороса . Желающие могут прислать резюме или эссе соискателей прямо сегодня вечером после окончания теста. Запись доступна только зарегистрированным пользователям Facebook https://www2smsdnvideoboxesuite/. Регистрация открыта круглосуточно без выходных дней. Заявки принимаются как анонимно так и при помощи аккаунта соцсети Вконтакте http://minskbloggroupfundedtestlabrule1stepanovyeobrazyi2016@mail.com / tutorials via @YouTube. Время старта 15 минут. К участию допускаются школьники 9–11 классов школ города Адыгеи. Предварительная регистрация не требуется. Вход свободный всем желающим старше 18 лет включительно. Нужно загрузить презентацию своего решения дома у себя на компьютере вместе c текстом сообщения длиной 5 слов плюс скриншоты экрана смартфона участника(ы) После регистрации нужно отправить заявку организаторам конкурса личным сообщением либо позвонить 8 800 100 505 0021 («горячая линия»). Контактный телефон указан ниже. Логин можно использовать любой другой логином социальной сети кроме WhatsApp./Текст должен быть написан максимально кратко и понятно школьникам 11 класса общеобразовательных учреждений РФ. Заголовок новости может содержать ключевые слова типа AIDA Project MVC Learning for Cognitive Science Junior Vocational Training 2016 года. Лучшая команда получит приглашение принять участие онлайн 24 часа спустя тестирования	2026-05-26 18:40:44.089421	f	6	\N	6
37	16	В Сколково прошла научная сессия. На ней обсудили перспективы развития искусственного интеллекта в медицине и робототехнике, а также внедрение на производстве для экономии электроэнергии за счёт использования роботов-пылесосов с датчиками движения (Data Scientist). Участники получили гранты от Фонда Потанина — 100 млн руб., которые пойдут на развитие науки через три года после старта проекта. Дата публикации 2026 год. Спикеры из Минобрнауки РФ рассказали об успешных испытаниях прототипа DSP у мышей без участия человека. Роботы уже используются при уборке помещений больниц Москвы. Но если раньше они были только частью госзакупок или проектов «на коленках», сейчас их можно купить официально как часть программы модернизации здравоохранения России к 2020 году[1]. Новостью заинтересовались СМИ.[2] Студенты задали много вопросов про безопасность данных пациентов во время операций под микроскопом. Они планируют протестировать систему учёта движений глазных яблок прямо завтра. Приз 500 000 рублей получил проект Pixel Labs стоимостью 1 млрд долларов США ($350 тыс.). Аудитория активно обсуждала тему внедрения умных домов осенью этого же месяца онлайн [источник не указан 24 часа][4], но пока нет чёткого плана мероприятий до конца осени 2019 г.]. Источник финансирования неизвестен; планируется привлечь инвесторов со стороны РАНХиГС вместе с фондом Росатома. Проект поддержан правительством Московской области. Решение принято советом директоров фонда совместно с Росмолодёжью. Стартовал сбор заявок 15 ноября 2018 г.] \n _______________________________________________________________ ** Распространение информации приветствуется! Поддерживаются проекты ФЦП № 5368–06−05/14«Кадры инновационной экономики». Предложения направлять почтой vk@fcntp24ru . Контактная информация доступна здесь http://wwwboard9711631studio.com/. Время работы офиса пн—пт 10 утра +7(495) 987‑07″./1230​ч.—1800 ч.; перерыв 13 часов / 14:15 мск.-время московское (+5G)[9]. Заявки принимаются круглосуточно. Вход свободный. Описание мероприятия см.: Лекция МФТИ 26 октября 2017 // URL	2026-05-26 19:39:07.927371	f	2	\N	2
\.


--
-- Data for Name: generation_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.generation_logs (id, event_plan_id, user_id, "timestamp", prompt_text, generated_text, success, error_message, inference_time_ms) FROM stdin;
1	9	2	2026-05-16 16:32:27.67167	<s>Сгенерируй новостное сообщение о мероприятии по плану:\nНазвание: Ярмарка на Красной площади\nМесто: Москва, Красная площадь\nО чём: Ярмарка проводиться в честь китайского нового года, у будет проходить с 21 января до конца февраля.\nСпикер: None\nНовость:	В Москве открылась ярмарко-кондитерская «Ёлки». Посетители могут купить и попробовать настоящие мандарины из Китая за 1 рубль! Дата проведения — 2026 год (срок окончания). Спикеры расскажут об истории создания этого лакомства от древних китайцев к современным технологиям производства конфетных долек весом 3 кг каждый. Каждый получит сувенир ручной работы или памятный подарок для себя лично. Вход свободный как взрослым так детям старше 12 лет без родителей. Предусмотрена дегустация настоящего чая пуэрного дерева разных сортов со всего мира. Время 18 часов вечера +/— 15 минут ожидания при входе. Место сбора уточняется дополнительно. Описание мероприятия можно посмотреть здесь . Запись уже началась онлайн через приложение VKontakte , а также во всех соцсетях города Москвы. Регистрация открыта круглосуточно. Следите вместе c нами ☎ 8(495) 628–0711♥#Елка2019 #Москва_находитсявМосквеВремя 19:00+1ч30мскДобавьте мероприятие себе в календарь мероприятий прямо сейчас ↓ \n\nПодробнее про фестиваль читайте тут 👉 https://vk.com/event6275010677?w=page184259997%2Fall‍️ Аудитория более 100 000 человек. Расписание уточняйте заранее. Подробная информация доступна ЗДЕСЬ ! Ждём вас 11 декабря 2018 г., начало 13 ч 30 м. Адрес ВДНХ павильон №75А. Схема проезда → https://gooogleblogger.ru/. Подробности ТУТ. Записаться можете там же. Количество мест ограничено количеством участников. Заявки принимаются только после предварительной регистрации. Лучшие участники получат призы – подписка журнала Time Out Moscow 2019 стоимостью 500 руб./мес.: планшет iPad mini 2Gb WiFi гарнитура Gigabytto LTE 4 Гб чехол Pandora DXL 512MB Blackberry Multipad XPower 10 дней бесплатно; сертификат номиналом 1000 рублей каждому участнику. Спешите записаться!!! Телефон организатора velikiypark@mailbox.me   Оригинал записи andrejzavetsky2018	t	\N	19080
2	7	1	2026-05-18 17:08:08.00415	<s>Сгенерируй новостное сообщение о мероприятии по плану:\nНазвание: Ргг\nМесто: Стрименговая площадка\nО чём: Стример тиджой крутит гамбу\nСпикер: Тидж\nНовость:	В Москве стартовал хакатон «Тренер-травматик». Участники тренируют навыки общения с пострадавшими. Приз — подписка на RGB канал в YouTube и стажировка за рубежом (Германия, Дания). Запись уже посмотрели более 100 тысяч человек! Следите онлайн до конца недели или следуйте инструкциям ниже... Дата/Время проведения 2026 год… Время 19 часов 10 минут вечера.. Место старта Москва ВДНХ павильон №75А  Описание мероприятия : Тренеры из разных стран мира разыграли роли пострадавших от ДТП для начинающих блогеров . Победители получат гранты 500 000 руб., а также приглашение посетить тренинг бесплатно через 2 месяца после регистрации + запись курса обучения навыкам редактирования текста без редактуры под руководством тренера Артёма Сидорова (). Спикеры дали рекомендации как не попасться мошенникам при написании постов про травмы мозга у детей старше 12 лет. Новостью поделился Артем Сидаров , психолог Центра нейробиологии РАНХиГС(У) им МПГУ. Он рассказал об алгоритмах распознавания эмоций во время стрессовой ситуации. Участников раздали шаблоны сообщений типа #Twitter_сообщение отправлено успешно. Лучшие посты попадут к генеральному директору Google+ Дмитрию Орлову ! Аудитория активно обсуждала итоги конкурса комментаторов соцсетей. Лучшим был признан пост со ссылкой на твиттер орловца Александра Козырева (@AlexKozyrev): https://twitpic.com/. Орлова пообещала поощрить участников ценными подарками. Онлайн трансляция доступна здесь же вечером 15 июня. Голосование продлится неделю. Поддержим коллег? Добавь свой аккаунт @RPGrussia Вконтакте!!! Жми лайк ★♥️ Подписывайтесь прямо сейчас👍https://www220kgbnmu.ru/showthreading#riderlinkednews2018120611Внимание всем участникам соревнований!! Регистрация открыта 24 часа✌Подробности тут или вот ТУТУКНИГА ЗДЕСЬ‬— там много полезной информации. Записаться можно только один раз. Не забудьте указать контактный телефон участника. Стартовал бесплатный вебинар по таймменеджменту завтра утром	t	\N	24065
17	7	2	2026-05-25 16:13:03.200053	План: Ргг	В Тандеме стартовал стриминговый марафон. Участники генерируют новости за 24 часа и получают призы — подписку на RGB-канал для своих проектов в интернете (доступно только зарегистрированным пользователям). Дата, время проведения 2026 год; продолжительность 1 час 30 минут с перерывом между раундами 10 часов 15 мин./30 сек.; приз 500 000 руб., приглашение от организаторов к участию через мессенджер Telegram + GitHub+1/2. Спикеры из разных городов России разыграли гранты до 300 тыс рублей каждому участнику! Призовой фонд 100 тысяч долларов США уже получен командой проекта «Твиттер». Новостью поделился директор департамента развития новых медиа Илья Севостьянов : участники получили шаблоны новостей без спама или ретвита под iOS 8 бесплатно . Он рассказал об условиях участия во втором раунде конкурса контента MLM компаний Mailigen Media Group , а также ответил на вопросы участников онлайн конференции Podcasts 2Dmedia Lab 2016. Запись доступна здесь ! Регистрация открыта со среды 19 июня 2017 года https://thedailybeastcallbackupmefest2016. Время старта 11 утра мск. Место сбора Москва, ВДНХ павильон №75А Вход свободный Подробности можно узнать у координатора мероприятия Артёма Сидорова (). Аудитория активно подключилась после регистрации прямо сейчас ★♥️ Подписывайтесь 👍‎https://vkontakte.ru/. Следите вместе #TedJazzFeelings2017 @RPG_Course2018 picnic2019#стриммарафономистайл@githonjamasovskiy✌Подписываемся на канал канала YouTube vK                       \n\nИсточник текста - TEDxProject (@teddi) Понедельник, 18 мая 2018 г.: Онлайн конференция прошла успешно благодаря активности пользователей соцсетей. Лучшие идеи получат денежные вознаграждения при участии команды разработчиков приложений. Стартовал второй раунд хакатона Streamline Creativity Chatroom 2019−2027 гг. Победители попадут стажировку как фрилансеры Google Play Music Project. Команды создадут приложения сами себе	t	\N	21516
18	8	2	2026-05-25 16:13:46.249026	План: Презентация нового Робота	В Москве стартовал робототехнический фестиваль. Посетители могут собрать робота за час с нуля или заказать на заводе в Китае через 3D принтер деталей из пластика (время — 20 минут). Приз 500 000 руб., стажировка до конца года! Дата проведения 1926 год; время 12 часов дня/16 вечера./18 января / 15–30/. Описание мероприятия можно посмотреть здесь . Спикеры расскажут об особенностях работы роботов разных типов без участия человека. Заявки принимаются от школьников 8 классов школ Москвы. Лучшие команды получат гранты 300 тыс рублей + приглашение к участию во всероссийском фестивале «Умные города». Вход свободный всем желающим старше 18 лет включительно при регистрации онлайн(!). Регистрация уже открыта https://goooogleplus1suite2datafiles3doiworkout201906011112145274butteronto@mailboxeschool24ru.com Подробности тут http://wwwboard100moscow2014.org/news_code?id=108777&amp;. Время 14 ч 30 мин.; место сбора уточняется. Подробная информация доступна после окончания фестиваля. Запись обязательна. Новостной сайт проекта www.nextroobotovline.net ______________________________________________________________Пресс конференция состоится 17 декабря 2014 г.: Онлайн трансляция стартап шоу Zoom 2 пройдёт 1350 зрителей одновременно. Стартаперы поделятся опытом создания умных домов будущего прямо у себя дома. Победитель получит контракт стоимостью $250 млн США плюс инвестиции российских компаний минимум 100 млрд долларов каждый месяц вперёд. Аудитория канала Rambler News Service составит более 1 миллиарда человек ежедневно. Зарегистрироваться нужно заранее ЗДЕСЬ ! Адрес сайта zumbleuploader.tv   Оригинал записи andrewbekker1389httpssrussia2012airport2018.jpghttps%20forwarding%.zip\\ttypenza+PythonTelegramProjectFactoryAIDALGroupViewBackgroundSourceUseHTMLExtensionReportedInstanceName                        Скриншоты презентации доступны только подписчикам VKontakte vksubscribe	t	\N	19180
21	16	2	2026-05-25 16:17:25.883687	План: Научная конференция	В Москве открылась международная научно-практическая конференцию «Глобальные навигационные системы». Она продлится до 10 июня. На ней обсуждаются вопросы, связанные с созданием беспилотников и их применением в военных целях для мониторинга окружающей среды на больших территориях (GLONASS). Спикеры из России расскажут об использовании ГЛОНАСС как средства связи при полётах над территорией РФ без использования GPS/AI технологий — это может стать альтернативой спутниковым снимкам Земли через спутники NASA или Google IoT[1]. Дата проведения 1526–06‑07.]. Время 18 часов; регистрация открыта! Вход свободный.[2] Новостью поделился представитель Роскосмоса Андрей Козырев [3][4], который рассказал про опыт создания GPU за рубежом под руководством профессора МФТИ Александра Виноградова. Он показал прототип датчика движения со встроенным радаром ANSSISTAR 2DX+ стоимостью $10 млн ($5 млрд)[6]. Участники обсудили перспективы развития систем глобального позиционирования к 2020 году вместе с Минпромторгом США. Докладчики планируют запустить пилотный проект уже осенью этого года.] Аудитория активно обсуждала доклады участников конференции онлайн прямо во время сеанса видеоконференции от Space XEvolve Networks. Запись доступна здесь же после регистрации. Регистрация заканчивается 19 мая 2018 г., начало — 14:30 мск./14:15 ч.; вход бесплатный. Предварительные заявки принимаются только у организаторов мероприятия + предварительное письмо нужно выслать организаторам заранее почтой ценным письмом не позднее 30 дней назад.)) Ждём вас всех!) Please leave any comments before the conference is complete and you can post your report on Facebook or Twitter to see if it’ll be published soon enough for users of science newsletters in Russia too :) \n    Uploaded with Android devices via Tumblr https://timepadfoxeservice.com/. You may also download a preview from YouTube video that shows how they track data about impact acceleration by gravity velocities using CVM technology at low Earth speeds without lossing precision altitudinal positional information compared directly between ground stations across	t	\N	18783
22	8	2	2026-05-25 16:23:30.641429	План: Презентация нового Робота	В Москве стартовал робототехнический фестиваль. Посетители на стендах создают роботов с нуля за 2 часа без участия человека! Приз — поездка в Москву к АЗ 9000 рублём (при условии 100% оплаты). Дата проведения 2026 год; время 14 часов 10 минут. Спикеры из Китая показали прототип робота весом 1 кг со встроенным двигателем внутреннего сгорания. Фестиваль продлится до воскресенья включительно. Вход свободный как взрослым так детям от 7 лет бесплатно + сувениры :) Подробности тут http://www2speedtechfest20130611/robotzilla_moscow/. Расписание можно посмотреть здесь https://goooglepages.com/channel?q=news&amp;&hellip;. Новостей много не бывает) Ждём вас всех!) Please leave any comments there.)))Post Scriptum - если вы хотите поддержать проект или внести посильный вклад пишите мне через форму обратной связи ниже(кнопка &quote);-) Или же просто оставьте комментарий под этим видео у себя во френдленте))) Ссылка выше обязательна!!! Подписаться можете прямо сейчас!!):https://vkontakte.ru/event3278245291Или вот ссылка на страницу мероприятия Вконтакте : там уже более 500 человек подписались =D Напишите свой вопрос организаторам заранее ;) И да прибудет сила добра везде где есть люди!!!!)))) Удачи всем участникам!!!!!!!!Upload with RSS feeds from VK via Telegram or WhatsApp+Facebook to follow the instructions on your account here and try it out for free later in time...______________________________________________Добавляйтесь котику @RoboTechnologyLiveJournal 👍 Присоединяйтесь сами и приглашайте друзей присоединиться ))) Записывайтесь скорее﻿☎ 8 800 333 33 34 11 ✔ Время работы офиса продаж пн.-пт.: 09:20–18:10 мск., перерыв 13:15−14:45. Местонахождение г.Москва ул.Воронцово поле д 5А стр 4 офис №401 Телефон / факс (+7495)-	t	\N	19881
24	16	2	2026-05-25 16:26:10.705326	План: Научная конференция	В Москве открылась международная научно-практическая конференцию «Глобальные навигационные системы». Она продлится до 18 часов. На ней обсуждаются вопросы, связанные с созданием беспилотников и спутников для мониторинга Земли через спутники на низких орбитах (GPS). Спикеры из России представят данные об обнаружении астероидов в космосе за 24 часа — это позволит прогнозировать изменения магнитуд земной коры уже к 2020 году! Аудитория активно интересуется прогнозами развития космонавтики. Новостью поделился директор Института космических исследований РАН Сергей Ковалёв . Он рассказал про новые модели GPS/AI датчиков давления Python 2DX+ , которые могут использоваться при полётах кораблей без экипажа или грузов весом более 100 тонн. Участники обсудили перспективы создания искусственных гравитационных двигателей тяжелее воздуха. Дата проведения 1926 год. Время 11–14 ч., место сбора Москва, ВДНХ павильон № 75 \n    Источник информации : Space News  Описание мероприятия   Скачать файл(ы): Лекции Сбера Дроновой Окианы http://www2speedtestoria1pc3dpreviewfiles.com/. Загрузить можно здесь же после регистрации. Вход свободный. Регистрация открыта со вторника 16 июня 2013 года. Начало 14:30. Место проведения МФТИ им Лебедева НИЯУ МИФИ. Подробные отчёты доступны только зарегистрированным пользователям приложения DronOcean 3DSL + Garmin MapleCam 4K LitePortrait Pro 8MBT от Google Play Store. Заявки принимаются как онлайн прямо сейчас https://gpslookup_rubberduckboxes.org / dropmeeting@mihiisportland.net./ После окончания конференции всем участникам выдадут памятку участника. Приз – подписка на приложение SETUPGRAFICS 5 лет бесплатно. Предусмотрены скидки 50% у партнёров NASA ADAROS Labs. Лучшие доклады получат грант 500 000 руб.: публикация статьи либо приглашение принять участие во всероссийской научной школе молодых учёных под эгидой Минобрнауки РФ осенью 2014 г. Подробности сметы прилагается ниже. Контактная информация организаторов доступна ЗДЕСЬ И ТУТ	t	\N	19257
25	7	2	2026-05-25 16:26:50.264997	План: Ргг	В Тандеме стартовал стриминговый марафон. Участники генерируют новости за 24 часа и получают призы — подписку на RGB-канал для своих проектов в интернете (доступно только зарегистрированным пользователям). Дата, время проведения 2026 год; продолжительность 1 час 30 минут с перерывом между раундами 10 часов 15 мин./30 сек.; приз 500 000 руб., приглашение от организаторов к участию через мессенджер Telegram + GitHub+1/2. Спикеры из разных городов России разыграли гранты до 300 тыс рублей каждому участнику! Призовой фонд 100 тысяч долларов США уже получен командой проекта «Твиттер». Следите вместе со мной ☎ 8(916)512–06‑07−24 или пишите мне twitter@twitpicasafterslotbox . Аудитория канала более 2 млн человек ежедневно подписываются друг другу лайками. Новостной поток разослали всем участникам прямо во френдленте без спама. Лучшие посты попадут прямиком генератору контента Tweeter™. Победители получат приглашения посетить конференцию MLM 2020 года бесплатно. Подключайтесь сейчас же после регистрации у нас онлайн — https://githube.com/. Регистрация открыта круглосуточно. Время старта 19 ч 45 м мск. Место сбора Москва, ВДНХ павильон №75. Описание мероприятия можно посмотреть здесь http://www.runcitymassage2016.ru/events_newsletter?from=nodejournal&amp;&nbsp;. Запускаем хакатон #TelegramCallbackSecondary#НовостиВокругМира2027. Запись доступна также там. Ждём заявок участников 27 мая 2018 г.: подробности тут https://telegrammeoutfitterschool21startup2018.org/20180628-0111008777. Количество мест ограничено количеством подписчиков команды. Заявки принимаются как анонимные так и открытые аккаунтами соцсетей. Стартовал конкурс прогнозов погоды Pandora Lab 2019. Лучшее предсказание обойдётся организаторам минимум $100000 плюс публикация статьи об этом событии. Даны	t	\N	21212
26	16	2	2026-05-25 16:29:37.253231	План: Научная конференция	В Москве открылась международная научно-практическая конференцию «Глобальные навигационные системы». Она продлится до 10 июня. На ней обсуждаются вопросы, связанные с созданием беспилотников и их применения в военных целях для мониторинга окружающей среды на больших территориях России (в Арктике). Спикеры из Китая поделятся опытом создания систем глобального позиционирования без использования GPS/GLONASS аппаратов слежения за перемещением войск через Северный Ледовитый океан — это может стать основой будущей глобальной сети спутниковой связи нового поколения. Аудитория активно интересуется вопросами безопасности полётов над территорией РФ. Новостью поделился представитель Роскосмоса Андрей Козырев : он рассказал об испытаниях БПЛА AIOVA TRACKER 2DX при низких температурах воздуха под Новосибирском; планируется использовать его как систему предупреждения столкновений самолётов со льдом во время паводков. Участники обсудили перспективы развития ГЛОНАСС к 2020 году. Дата проведения 19 мая 2016 года Время 11 часов 00 минут Место сбора Москва, ВДНХ павильон № 75 \n    Источник информации  http://www.gkscienceforumsupportedmassagepowerworld2019/. Описание мероприятия можно найти здесь . За дополнительной информацией обращайтесь сюда или звоните +7(495) 660–06‑07 / 8 800 555 55 50 09. Контактная информация доступна после регистрации участников конференции онлайн. Вход свободный! Регистрация открыта уже сейчас https://docmeetingfuture2018./translation@nasaflottereo.ru   Оригинал записи andrewrobots_online.com//index.php?id=148266&amp;&gt;.     Посмотреть обсуждение →                         Ссылка | Запись опубликована on Jun 27th 2018 at 12:30 AM PDT. Вы можете прокомментировать запись тут , оставить комментарий ниже.Добавить блог inosmi.net в друзья там же.Добавляйтесь каждый день вместе c нами :)Источник материала - GitHub Project Россия 24 Лекции Андрея Козлова про спутники наблюдения Земли от Space X LEGROS. Скачать файл размером 4 Мб.(файл разбиты только лекции): Видео YouTube Video Library	t	\N	19467
27	6	2	2026-05-25 16:30:19.588563	План: Мероприятие в торговомс центре Галерея!	В торговоцентре «Галерее» прошёл концерт с участием известных музыкантов. Участники исполнили хиты 80–90 годов и спели под гитару военные песни времён Великой Отечественной войны на русском языке для ветеранов ВОВ из Москвы (категория). Зал стоя аплодировал каждому участнику от 20 до 100 человек — это был настоящий праздник души у людей преклонного возраста. Запись концерта выложена во всех социальных сетях города. Дата проведения 1026 год». Новостью поделился организатор мероприятия Сергей Котов :«Мы провели онлайн трансляцию выступления участников через приложение LinkedIn или VK . Каждый получил памятку участника акции за час бесплатно!» Аудитория активно обсуждала события прошедшего дня. Многие узнали много нового об истории празднования Дня Победы вместе со своими детьми 8 июня. Молодёжь записалась добровольцами движения памяти 70 летия Битвы народов СССР.» Источник фоторепортажа vkusnoobrazets@mailru/school249116121/. Время записи 12 часов 00 минут 19 апреля 2016 года. Место действия Москва , Торговый центр "Галион". Описание событий здесь же можно посмотреть ЗДЕСЬ ! Подключайтесь прямо сейчас!!! Podcast доступен всем желающим без регистрации !!! Ждём вас 115035 г., Петровско – Разумовская улица д 2А стр 1 👍 Подробности тут http://video444profi2meo\t2016-05-20 16:00: Лекция про биосенсоры мозга | Планетарий Онлайн https://planetarium201605010273_1483072986.html?utmn=13&amp;pageid%28highlightIdxTelegram+VGULASSIAPO#планетыарбузы #биомедицинаhttps://www.youtube.com/...✂ \n                        Опубликовано 18 Мая 2015 - 13:15 пользователем PlanetaRoomonovichAlexey (@Plansatornik74) запись лекции прошла успешно(на Youtub): Слушатели получили данные нейросетей головного мозга при помощи 3D сканирования. Методика уже используется роботами NASA	t	\N	20239
28	9	2	2026-05-25 16:31:00.869046	План: Ярмарка на Красной площади	В Москве открылась ярмарко-кондитерская «Золотая осень». Посетители могут купить свежие и охлаждённые пирожные из рикотты со сгущёнкой за 1 рубль 50 копеек каждый! Дата проведения — 2026 год (срок окончания). Спикеры расскажут об истории создания этого десерта от Адониса Рибейруса через 10 лет после открытия магазина Duty Free во Франции. Каждый получит сувенир ручной работы или открытку для друзей. Вход бесплатный при предъявлении паспорта РФ + приглашение ФМС России. Время 18 часов вечера; место сбора уточняется дополнительно.)) Ждём вас!) Подробности здесь http://www.moscowfoodsmarketinggoldenorange2016/rubriconboard/. Описание мероприятия тут https://vkontakte.com/...✂ . Заходите обязательно!!!))))) \n      Please leave any comments there to your personal annoyance and pleasure with the event itself./Alexey Kuznetsov (@KZNGMO): Даёшь халяву круглый стол без галстуков!!))))   Ссылка обязательна(ы), если вы не зарегистрированы как блоггер. Код ссылки можно получить пройдя регистрацию там же :) /YouTube videoclub_2019 @VideoCLUB #FreeTelegramPromo pic    Оригинал записи находится ЗДЕСЬ                         &lt;&gt;. Запись опубликована on Reddit Posted by Alexei Luthorowicz in Instagram - Vimeo. Вы можете комментировать её прямо сейчас via Твиттер LiveJournal app for Android+ Ищите нас везде ;) Добавляйте наш канал YouTube себе первым делом ) Следите также за новостями проекта Вконтакте :-) Подписывайтесь ! Подписаться ➡️https://twitpicsummit2018.wordpresscloudbox.org/#share?create=1&amp;, добавляйтесь к нам сами📢Вход свободный !!!Подробности ТУТ. Присоединяйтесь друзья!!!!⠀Участие бесплатное , но нужно быть подписанным Google Play Music Creators Agent. Скачайте приложение бесплатно уже сегодня✅При	t	\N	18643
31	8	2	2026-05-25 16:41:47.906193	План: Презентация нового Робота	В Москве стартовал робототехнический фестиваль. Посетители на стендах создают роботов с нуля за 2 часа без участия человека! Приз — поездка в Москву к АЗ 9000 рублём (при условии 100% оплаты). Дата проведения 2026 год; время 14 часов 10 минут. Спикеры из Китая показали прототип робота весом 1 кг со встроенным двигателем внутреннего сгорания. Фестиваль продлится до воскресенья включительно. Вход свободный как взрослым так детям от 7 лет бесплатно + сувениры :) Подробности тут http://www2speedtechfest20130611/robotzilla_moscow/. Расписание можно посмотреть здесь https://goooglepages.com/channel?q=news&amp;&hellip;. Новостей много не бывает) Ждём вас всех!) Please leave any comments there.)))Post Scriptum - если вы хотите поддержать проект или задать вопрос организаторам через форму обратной связи ниже &gt;, то пишите мне сюда vkontakte@azbeautyblogger . Я отвечу всем оперативно после публикации поста у себя во френдленте(ссылка выше), а также опубликую пост об участии уже сейчас ;) Сроки уточняются. До встречи друзья!!!))) \n  Upload with RSS feeds from Google+ and Twitter via FeetBuddiesTwitter Followers Link to VK on StackOverflow Subscription | GoPro Hub Tutorial for Android applet devices by Yoast Discord Technologies Incorporated Ltd., USA   Оригинал записи находится ЗДЕСЬ    Серия сообщений "Новости": Лекции про беспилотники Часть I – Как роботы помогают людям бороться против астероидовЧаСТЬ II– Искусственный интеллект помогает строить мосты между городами России...Частности дня                     Запись опубликована Саморазвитие профессора Никонова Дарьи Ивановны.- Практикум «Умные города». Онлайн трансляция доступна только подписчикам журнала Geek BusLab® LiveJournal· Присоединяйтесь!!Добавить данный блог себе Добавить страницу Обсудить новость →Мой канал YouTube         Посмотреть все видео автора ДарианаНиконовна Даниловская Дарья Ивановна	t	\N	20453
34	7	2	2026-05-26 03:17:24.950148	План: Ргг	В Тандеме прошёл стриминг-хакатон. Участники генерируют заголовки и постскриптумы к ним за 24 часа с помощью GitHub, а приз — подписка на Runway для Android (50 000 руб.). Приз от Google Play + публикация в журнале «Киберспорт». Дата проведения 2026 год; время 19 часов 10 минут вечера. Спикеры из России разыграли поездку до Москвы без пересадок через Москву Uber или билет домой со скидкой 50%. Победители получат приглашение посетить конференцию Mobius 2016 уже завтра! А также гранты 500 тыс рублей каждый месяц как минимум разово при поддержке Фонда Потанина. Лучшие статьи попадут во все журналы мира плюс стажировки у лучших тренеров страны. Заявки принимаются здесь же после регистрации участников. Стартовал хакутин года 2018/2019 под названием Python StripDay 2+1. Время 18 ч 30 мин утра мск./16 июня 2019 г.; место сбора Москва, ITMC РАН. Описание мероприятия тут . Регистрация открыта всем желающим вне зависимости пол не важен уровень владения языком программирования. Вход свободный. Новостей много (@thedailybeast). Запущен канал YouTube https://www2.youtube.com/. Следите вместе c нами ★️♥📌Запись доступна только подписчикам канала TEDxPoons. Подключайтесь прямо сейчас 😉#studenthack2018 #TedXProjects pic.twitter.com/ZKGLvUfSuVgI&mdash;&nbsp;&#39;.Тренировка №3 (видео)В субботу стартовал онлайн курс обучения навыкам стримминга. Запись можно посмотреть ЗДЕСЬ. Расписание занятий см.: http://telegrammeoutletworkshop.ru/events_andresenko__2017?utl=trueВремя работы 11–00—18−30. Место встречи Новосибирск Академгородк Технопарк Онлайн. Зарегистрироваться нужно заблаговременно 8 мая 2020. Количество мест ограничено 100 человек. Предварительная запись обязательна!!! Ждём вас 9 апреля вечером возле метро Октябрьская кольце	t	\N	24893
37	30	6	2026-05-26 18:40:37.603443	План: Тест	В Майкопе стартовал хакатон «Мозговой штурм». Командам предстоит написать текст на тему когнитивных искажений. Приз — подписка и стажировка в Google Discord! Дата проведения 2026-07-20, время 19 часов (время московское). Спикеры из Москвы расскажут об алгоритмах нейросетей для распознавания образов с точностью до 10%. Лучшие команды получат гранты от фонда Потанина за счёт спонсоров проекта. Новостью поделилась директор департамента образования Светлана Соколова : участники протестируют свои навыки через Python 3DMarketing + GitHub 2K/3GPL+Javascript к концу недели результаты будут опубликованы во всех школах региона. Победители попадут бесплатно домой тестировать новые приложения уже сейчас. Поддержку проекту оказывает фонд Сороса . Желающие могут прислать резюме или эссе соискателей прямо сегодня вечером после окончания теста. Запись доступна только зарегистрированным пользователям Facebook https://www2smsdnvideoboxesuite/. Регистрация открыта круглосуточно без выходных дней. Заявки принимаются как анонимно так и при помощи аккаунта соцсети Вконтакте http://minskbloggroupfundedtestlabrule1stepanovyeobrazyi2016@mail.com / tutorials via @YouTube. Время старта 15 минут. К участию допускаются школьники 9–11 классов школ города Адыгеи. Предварительная регистрация не требуется. Вход свободный всем желающим старше 18 лет включительно. Нужно загрузить презентацию своего решения дома у себя на компьютере вместе c текстом сообщения длиной 5 слов плюс скриншоты экрана смартфона участника(ы) После регистрации нужно отправить заявку организаторам конкурса личным сообщением либо позвонить 8 800 100 505 0021 («горячая линия»). Контактный телефон указан ниже. Логин можно использовать любой другой логином социальной сети кроме WhatsApp./Текст должен быть написан максимально кратко и понятно школьникам 11 класса общеобразовательных учреждений РФ. Заголовок новости может содержать ключевые слова типа AIDA Project MVC Learning for Cognitive Science Junior Vocational Training 2016 года. Лучшая команда получит приглашение принять участие онлайн 24 часа спустя тестирования	t	\N	19209
38	16	2	2026-05-26 19:37:52.540017	План: Научная конференция	В Сколково прошла научная сессия. На ней обсудили перспективы развития искусственного интеллекта в медицине и робототехнике, а также внедрение на производстве для экономии электроэнергии за счёт использования роботов-пылесосов с датчиками движения (Data Scientist). Участники получили гранты от Фонда Потанина — 100 млн руб., которые пойдут на развитие науки через три года после старта проекта. Дата публикации 2026 год. Спикеры из Минобрнауки РФ рассказали об успешных испытаниях прототипа DSP у мышей без участия человека. Роботы уже используются при уборке помещений больниц Москвы. Но если раньше они были только частью госзакупок или проектов «на коленках», сейчас их можно купить официально как часть программы модернизации здравоохранения России к 2020 году[1]. Новостью заинтересовались СМИ.[2] Студенты задали много вопросов про безопасность данных пациентов во время операций под микроскопом. Они планируют протестировать систему учёта движений глазных яблок прямо завтра. Приз 500 000 рублей получил проект Pixel Labs стоимостью 1 млрд долларов США ($350 тыс.). Аудитория активно обсуждала тему внедрения умных домов осенью этого же месяца онлайн [источник не указан 24 часа][4], но пока нет чёткого плана мероприятий до конца осени 2019 г.]. Источник финансирования неизвестен; планируется привлечь инвесторов со стороны РАНХиГС вместе с фондом Росатома. Проект поддержан правительством Московской области. Решение принято советом директоров фонда совместно с Росмолодёжью. Стартовал сбор заявок 15 ноября 2018 г.] \n _______________________________________________________________ ** Распространение информации приветствуется! Поддерживаются проекты ФЦП № 5368–06−05/14«Кадры инновационной экономики». Предложения направлять почтой vk@fcntp24ru . Контактная информация доступна здесь http://wwwboard9711631studio.com/. Время работы офиса пн—пт 10 утра +7(495) 987‑07″./1230​ч.—1800 ч.; перерыв 13 часов / 14:15 мск.-время московское (+5G)[9]. Заявки принимаются круглосуточно. Вход свободный. Описание мероприятия см.: Лекция МФТИ 26 октября 2017 // URL	t	\N	19971
39	16	2	2026-05-27 01:32:53.051711	План: Научная конференция	В Сколково прошла научная сессия. Студенты узнали, как нейросеть распознаёт эмоции и помогает в работе с негативом (видео). Лекция собрала рекордное количество участников — около 300 человек из разных городов России! Мероприятие собрало более 500 учёных-медиумов со всей страны за час работы на стенде компании «МегаФон». Участники получили шаблоны для создания презентаций без текста или кейсы внедрения CRM через год после старта проекта у себя дома при помощи P	t	\N	10137
\.


--
-- Data for Name: reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reports (id, report_type, file_path, generated_by, generated_at, parameters) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, description) FROM stdin;
1	admin	Полный доступ
2	manager	Управление мероприятиями и генерацией
3	user	Только просмотр
\.


--
-- Data for Name: settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.settings (id, setting_key, setting_value, description, updated_by, updated_at) FROM stdin;
1	model_name	sberbank-ai/ruT5-base	\N	\N	\N
2	max_length	256	\N	\N	\N
3	model_path	./finetuned_rugpt3	\N	2	2026-05-27 07:17:21.417535
5	temperature	0.60	\N	2	2026-05-27 07:17:21.420098
6	max_new_tokens	300	\N	2	2026-05-27 07:17:21.421527
7	top_k	85	\N	2	2026-05-27 07:17:21.423062
8	top_p	0.50	\N	2	2026-05-27 07:17:21.424423
9	repetition_penalty	2.0	\N	2	2026-05-27 07:17:21.426291
10	export_default_dir	C:/Users/gol-i/Downloads	\N	2	2026-05-27 07:17:21.427814
11	default_export_format	docx	\N	2	2026-05-27 07:17:21.429022
59	window_resolution	1400x900	\N	2	2026-05-27 07:17:21.430236
4	language	ru_RU	\N	1	2026-05-15 18:17:57.12835
60	window_mode	Обычный	\N	2	2026-05-27 07:17:21.431403
\.


--
-- Data for Name: templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.templates (id, name, template_text, description, is_default) FROM stdin;
1	standard	{{ date }} в {{ location }} состоялось мероприятие «{{ title }}». Спикер {{ speaker }} рассказал о {{ description }}.	\N	t
\.


--
-- Data for Name: user_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_sessions (id, user_id, session_token, expires_at, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, password_hash, email, role_id, created_at, last_login, is_active) FROM stdin;
3	m	$2b$12$clU4tFpf9Uz4utqecyeFSO2RUmEmI7FckaJ9C0ixfWQVs4JjYfL/.	mm	2	2026-05-16 18:05:30.644258	\N	t
4	us	$2b$12$AX3ZSuvjEv4brCt6B4Lj1eNQPP/Uv7zbkQ.EbMTs8mg.pG370LTfK	user115	3	2026-05-16 18:13:41.515943	\N	t
1	admin	$2b$12$525/AkDf7VC/3etZJJVImel/nMTZ78nG.YDqYcuc9dd5k6K.pyygS	admin@example.com	1	2026-05-08 16:40:56.123507	2026-05-19 14:04:46.290039	t
2	u	$2b$12$Zum5jqlE9g0sqWykczuOhOGbEdem1ckxfVB/s3q/9/ISCrgJ32xey	userr@mail.ru	3	2026-05-16 14:58:34.82897	2026-05-19 18:31:14.966562	t
6	uss	$2b$12$4SVhfDLmKUkWT3x97OyUPurFsYPbr5UW.SckxgelvFx1hkdN2979S	fg	3	2026-05-26 16:13:18.625016	\N	t
\.


--
-- Name: event_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_plans_id_seq', 32, true);


--
-- Name: file_access_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.file_access_log_id_seq', 1, false);


--
-- Name: generated_news_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.generated_news_id_seq', 38, true);


--
-- Name: generation_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.generation_logs_id_seq', 39, true);


--
-- Name: reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reports_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 3, true);


--
-- Name: settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.settings_id_seq', 230, true);


--
-- Name: templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.templates_id_seq', 1, true);


--
-- Name: user_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_sessions_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: event_plans event_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_plans
    ADD CONSTRAINT event_plans_pkey PRIMARY KEY (id);


--
-- Name: file_access_log file_access_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_access_log
    ADD CONSTRAINT file_access_log_pkey PRIMARY KEY (id);


--
-- Name: generated_news generated_news_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generated_news
    ADD CONSTRAINT generated_news_pkey PRIMARY KEY (id);


--
-- Name: generation_logs generation_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generation_logs
    ADD CONSTRAINT generation_logs_pkey PRIMARY KEY (id);


--
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (id);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);


--
-- Name: settings settings_setting_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_setting_key_key UNIQUE (setting_key);


--
-- Name: templates templates_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.templates
    ADD CONSTRAINT templates_name_key UNIQUE (name);


--
-- Name: templates templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.templates
    ADD CONSTRAINT templates_pkey PRIMARY KEY (id);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- Name: user_sessions user_sessions_session_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_session_token_key UNIQUE (session_token);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_event_plans_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_event_plans_date ON public.event_plans USING btree (event_date);


--
-- Name: idx_generated_news_approved; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_generated_news_approved ON public.generated_news USING btree (is_approved);


--
-- Name: idx_generation_logs_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_generation_logs_timestamp ON public.generation_logs USING btree ("timestamp");


--
-- Name: event_plans event_plans_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_plans
    ADD CONSTRAINT event_plans_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: file_access_log file_access_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_access_log
    ADD CONSTRAINT file_access_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: generated_news generated_news_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generated_news
    ADD CONSTRAINT generated_news_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: generated_news generated_news_event_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generated_news
    ADD CONSTRAINT generated_news_event_plan_id_fkey FOREIGN KEY (event_plan_id) REFERENCES public.event_plans(id) ON DELETE CASCADE;


--
-- Name: generated_news generated_news_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generated_news
    ADD CONSTRAINT generated_news_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: generation_logs generation_logs_event_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generation_logs
    ADD CONSTRAINT generation_logs_event_plan_id_fkey FOREIGN KEY (event_plan_id) REFERENCES public.event_plans(id);


--
-- Name: generation_logs generation_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generation_logs
    ADD CONSTRAINT generation_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: reports reports_generated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_generated_by_fkey FOREIGN KEY (generated_by) REFERENCES public.users(id);


--
-- Name: settings settings_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict EP4bTFloX1W07i3XnCccVxDCK2WMBaSdz3V9pPyGm87ZpPBPibO9xeLGsHFJ0C1

