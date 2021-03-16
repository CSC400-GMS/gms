
CREATE TABLE if not exists account(
  email VARCHAR(255) NOT NULL,
  pass VARCHAR(255) NOT NULL,
  account VARCHAR(255) NOT NULL,
  PRIMARY KEY (email)
);

CREATE TABLE if not exists admin(
  id_num INTEGER NOT NULL,
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  lastname VARCHAR(255) NOT NULL,
  PRIMARY KEY (id_num),
  foreign KEY (email) references account(email)
);

CREATE TABLE if not exists reviewer(
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  lastname VARCHAR(255) NOT NULL,
  PRIMARY KEY(email),
  foreign KEY (email) references account(email)
);

CREATE TABLE if not exists researcher(
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  lastname VARCHAR(255) NOT NULL,
  status VARCHAR(255),
  dept VARCHAR(255),
  PRIMARY KEY(email),
  foreign KEY (email) references account(email)
);

CREATE TABLE if not exists proposals(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title VARCHAR(255) NOT NULL,
  summary VARCHAR(255) NOT NULL,
  needs VARCHAR(255) NOT NULL,
  goals VARCHAR(255) NOT NULL,
  timeline VARCHAR(255) NOT NULL,
  funding_re INTEGER NOT NULL,
  budget VARCHAR(255) NOT NULL,
  grant_id INTEGER NOT NULL,
  date_submitted datetime NOT NULL,
  approved binary,
  approved_by INTEGER,
  submitted_by VARCHAR(255) NOT NULL,
  assigned_reviewer VARCHAR(255),
  foreign KEY(assigned_reviewer) references reviewer(user_name),
  foreign KEY(submitted_by) references researcher(user_name),
  foreign KEY(grant_id) references grants(id),
  foreign KEY(approved_by) references admin(id_num)
);

CREATE TABLE if not exists reports(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  proposal_id int NOT NULL,
  reviewer varchar(255) NOT NULL,
  assigned_by int,
  FOREIGN KEY(reviewer) references reviewer(user_name),
  FOREIGN KEY(proposal_id) references proposals(id)
);

CREATE TABLE if not exists report_info(
  id INTEGER PRIMARY KEY,
  score INTEGER NOT NULL,
  comments varchar(255) NOT NULL,
  FOREIGN KEY (id) references reports(id)
);

CREATE TABLE if not exists grants(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title VARCHAR(255) NOT NULL,
  fund INTEGER NOT NULL,
  sponsor VARCHAR(255) NOT NULL,
  requirements VARCHAR(255) NOT NULL,
  post_date datetime NOT NULL,
  submition_deadline datetime NOT NULL,
  added_by VARCHAR(255) NOT NULL,
  FOREIGN KEY(added_by) references admin(id_num)
);
