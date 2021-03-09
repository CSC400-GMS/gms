
CREATE TABLE if not exists account(
  email VARCHAR(255) NOT NULL,
  pass VARCHAR(255) NOT NULL,
  account VARCHAR(255) NOT NULL,
  PRIMARY KEY (email)
);

CREATE TABLE if not exists admin(
  id_num int NOT NULL,
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
  PRIMARY KEY(email),
  foreign KEY (email) references account(email)
);

CREATE TABLE if not exists proposals(
  id int auto_increment,
  title VARCHAR(255) NOT NULL,
  application VARCHAR(255) NOT NULL,
  grant_id int NOT NULL,
  date_submitted datetime NOT NULL,
  approved binary,
  submitted_by VARCHAR(255) NOT NULL,
  assigned_reviewer VARCHAR(255),
  PRIMARY KEY(id),
  foreign KEY(assigned_reviewer) references reviewer(user_name),
  foreign KEY(submitted_by) references researcher(user_name),
  foreign KEY(grant_id) references grants(id)
);

CREATE TABLE if not exists reports(
  id int auto_increment,
  score int NOT NULL,
  comments varchar(255) NOT NULL,
  proposal_id int NOT NULL,
  reviewer varchar(255) NOT NULL,
  PRIMARY KEY(id),
  FOREIGN KEY(reviewer) references reviewer(user_name),
  FOREIGN KEY(proposal_id) references proposals(id)
);

CREATE TABLE if not exists grants(
  id int auto_increment NOT NULL,
  title VARCHAR(255) NOT NULL,
  sponsor VARCHAR(255) NOT NULL,
  requirements VARCHAR(255) NOT NULL,
  post_date datetime NOT NULL,
  submition_deadline datetime NOT NULL,
  added_by VARCHAR(255) NOT NULL,
  PRIMARY KEY(id),
  FOREIGN KEY(added_by) references admin(id_num)
);
