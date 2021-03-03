
CREATE TABLE account(
  email VARCHAR(255),
  pass VARCHAR(255),
  name VARCHAR(255),
  lastname VARCHAR(255),
  PRIMARY KEY (email)
);

CREATE TABLE admin(
  id_num int,
  email VARCHAR(255),
  PRIMARY KEY (id_num),
  foreign KEY (email) references account(email)
);

CREATE TABLE reviewer(
  user_name VARCHAR(255),
  email VARCHAR(255),
  PRIMARY KEY(user_name),
  foreign KEY (email) references account(email)
);

CREATE TABLE researcher(
  user_name VARCHAR(255),
  email VARCHAR(255),
  orginization VARCHAR(255),
  PRIMARY KEY(user_name),
  foreign KEY (email) references account(email)
);

CREATE TABLE proposals(
  id int auto_increment,
  title VARCHAR(255),
  application VARCHAR(255),
  grant_id int,
  date_submitted datetime,
  approved binary,
  submitted_by VARCHAR(255),
  assigned_reviewer VARCHAR(255),
  PRIMARY KEY(id),
  foreign KEY(assigned_reviewer) references reviewer(user_name),
  foreign KEY(submitted_by) references researcher(user_name),
  foreign KEY(grant_id) references grants(id)
);

CREATE TABLE reports(
  id int auto_increment,
  score int,
  comments varchar(255),
  proposal_id int,
  reviewer varchar(255),
  PRIMARY KEY(id),
  FOREIGN KEY(reviewer) references reviewer(user_name),
  FOREIGN KEY(proposal_id) references proposals(id)
);

CREATE TABLE grants(
  id int auto_increment,
  title VARCHAR(255),
  submition_deadline datetime,
  requirements VARCHAR(255),
  added_by VARCHAR(255),
  PRIMARY KEY(id),
  FOREIGN KEY(added_by) references admin(id_num)
);
