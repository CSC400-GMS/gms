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
  dept VARCHAR(50) NOT NULL,
  PRIMARY KEY (id_num),
  foreign KEY (email) references account(email)
);

CREATE TABLE if not exists reviewer(
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  lastname VARCHAR(255) NOT NULL,
  dept VARCHAR(50) NOT NULL,
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
  workplan VARCHAR(255) NOT NULL,
  significance VARCHAR(255) NOT NULL,
  outcome VARCHAR(255) NOT NULL,
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
  signifigance INTEGER NOT NULL,
  work_plan INTEGER NOT NULL,
  outcomes INTEGER NOT NULL,
  budget_proposal INTEGER NOT NULL,
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
  dept VARCHAR(50) NOT NULL,
  FOREIGN KEY(added_by) references admin(id_num)
);

CREATE TABLE if not exists tags(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tag VARCHAR(255) NOT NULL
);

CREATE TABLE if not exists tagged_proposals(
  tag VARCHAR(255) NOT NULL,
  proposal_id INTEGER NOT NULL,
  FOREIGN KEY(tag) references tags(id),
  FOREIGN KEY(proposal_id) references proposals(id),
  PRIMARY KEY(tag, proposal_id)
);

INSERT INTO tags(tag) VALUES ('Accelerators');
INSERT INTO tags(tag) VALUES ('Agile Methods');
INSERT INTO tags(tag) VALUES ('Algorithms');
INSERT INTO tags(tag) VALUES ('Animation');
INSERT INTO tags(tag) VALUES ('Aspect-oriented Programming');
INSERT INTO tags(tag) VALUES ('Assistive Technology');
INSERT INTO tags(tag) VALUES ('Automated Theorem Proving');
INSERT INTO tags(tag) VALUES ('Bioinformatics');
INSERT INTO tags(tag) VALUES ('Biomechanical Modeling');
INSERT INTO tags(tag) VALUES ('Biostatistics');
INSERT INTO tags(tag) VALUES ('Cloud computing Security');
INSERT INTO tags(tag) VALUES ('Computational Genetics');
INSERT INTO tags(tag) VALUES ('Computer Architecture');
INSERT INTO tags(tag) VALUES ('Computer Graphics');
INSERT INTO tags(tag) VALUES ('Concurrency');
INSERT INTO tags(tag) VALUES ('Control Theory');
INSERT INTO tags(tag) VALUES ('Cyberinfrastructure');
INSERT INTO tags(tag) VALUES ('Data integration');
INSERT INTO tags(tag) VALUES ('Data Mining');
INSERT INTO tags(tag) VALUES ('Diffusion Imaging');
INSERT INTO tags(tag) VALUES ('Distributed Systems');
INSERT INTO tags(tag) VALUES ('Embedded Systems');
INSERT INTO tags(tag) VALUES ('Energy-efficient Computing');
INSERT INTO tags(tag) VALUES ('File Systems');
INSERT INTO tags(tag) VALUES ('Graphics Hardware');
INSERT INTO tags(tag) VALUES ('Haptics');
INSERT INTO tags(tag) VALUES ('Hardware Security');
INSERT INTO tags(tag) VALUES ('High-Performance Computing');
INSERT INTO tags(tag) VALUES ('Human-Computer Interaction');
INSERT INTO tags(tag) VALUES ('Internet of Things');
INSERT INTO tags(tag) VALUES ('Machine Learning');
INSERT INTO tags(tag) VALUES ('Medical Image Analysis');
INSERT INTO tags(tag) VALUES ('Mobile Computing');
INSERT INTO tags(tag) VALUES ('Modeling	Multimedia Systems');
INSERT INTO tags(tag) VALUES ('Network Protocols');
INSERT INTO tags(tag) VALUES ('Network Security');
INSERT INTO tags(tag) VALUES ('Networking');
INSERT INTO tags(tag) VALUES ('Operating Systems');
INSERT INTO tags(tag) VALUES ('Parallel Algorithms');
INSERT INTO tags(tag) VALUES ('Performance Analysis');
INSERT INTO tags(tag) VALUES ('Real-time Systems');
INSERT INTO tags(tag) VALUES ('Rendering');
INSERT INTO tags(tag) VALUES ('Scientific Computing');
INSERT INTO tags(tag) VALUES ('Security');
INSERT INTO tags(tag) VALUES ('Sensor Systems');
INSERT INTO tags(tag) VALUES ('Shape Analysis');
INSERT INTO tags(tag) VALUES ('Simulation');
INSERT INTO tags(tag) VALUES ('Software');
INSERT INTO tags(tag) VALUES ('Sound and Audio Display');
INSERT INTO tags(tag) VALUES ('Statistical Genetics');
INSERT INTO tags(tag) VALUES ('Tracking');
INSERT INTO tags(tag) VALUES ('Virtual Environments');
INSERT INTO tags(tag) VALUES ('Virtualization');
INSERT INTO tags(tag) VALUES ('Visual Analytics');

