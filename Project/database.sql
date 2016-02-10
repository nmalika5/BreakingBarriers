CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(64),
    password VARCHAR(64),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    lang_id INTEGER REFERENCES languages(lang_id) NOT NULL,
    phone_number VARCHAR(50), NOT NULL
);

CREATE TABLE languages (
    lang_id SERIAL PRIMARY KEY,
    lang_name VARCHAR(30) NOT NULL,
    yandex_lang_code VARCHAR(2), NOT NULL
);

CREATE TABLE contacts (
    contact_id SERIAL PRIMARY KEY,
    contact_first_name VARCHAR(64),
    contact_last_name VARCHAR(64),
    contact_phone VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES users(user_id) NOT NULL,
    lang_id INTEGER REFERENCES languages(lang_id) NOT NULL
);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    message_text VARCHAR(200),
    message_status VARCHAR(20),
    message_sent_at DATETIME,
    user_id INTEGER REFERENCES users(user_id)
);

CREATE TABLE messages_langs (
    message_lang_id SERIAL PRIMARY KEY,
    lang_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL
);

CREATE TABLE messages_contacts (
    message_contact_id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(contact_id) NOT NULL,
    message_id INTEGER REFERENCES messages(message_id) NOT NULL
);


INSERT INTO users (email, password, first_name, last_name, phone_number, lang_id)
VALUES ('test@test.com', 'test', 'English', 'Test', '(555) 555-5555', 1),
('test2@test.com', 'test', 'Spanish', 'Test', '(415) 555-5555', 2),
('test3@test.com', 'test', 'Russian', 'Test', '(510) 555-5555', 5),
('test4@test.com', 'test', 'French', 'Test', '(650) 555-5555', 4);

INSERT INTO languages (lang_name, yandex_lang_code) VALUES
('English', 'en'),
('Spanish', 'es'),
('Persian', 'fa'),
('French', 'fr'),
('Russian', 'ru'),
('Tajik', 'tg');

INSERT INTO contacts (contact_first_name, contact_last_name, contact_phone, user_id, 
                      lang_id)
VALUES ('Contact', 'Test', '(410) 555-5555', 1, 1),
('Contact2', 'Test', '(413) 555-5555', 1, 1),
('Contact3', 'Test', '(408) 555-5555', 3, 5),
('Contact4', 'Test', '(212) 555-5555', 3, 5),
('Contact4', 'Test', '(212) 555-5555', 4, 4),
('Contact4', 'Test', '(212) 555-5555', 2, 2),
('Contact4', 'Test', '(212) 555-5555', 2, 2);

INSERT INTO messages (message_text, message_status, message_sent_at, user_id, original_lang_id)
VALUES ('This is an english test message', 1, NULL, 1, 1),
('This is a russian test message', 3, '2015-02-07', 3, 5);

INSERT INTO messages_langs (lang_id, message_id)
VALUES (1, 1), (5, 2);

INSERT INTO messages_contacts (contact_id, message_id)
VALUES (1, 1), (2, 1), (3, 2), (4, 2);





