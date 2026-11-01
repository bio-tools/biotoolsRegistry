USE elixir;

UPDATE django_site set domain='http://localhost:8000', name='bio.tools local server' where id = 1;

-- required for "issue" code to work
INSERT INTO `elixir_issuestate` (`id`, `name`, `description`)
VALUES
	(1, 'fail', NULL),
	(2, 'fixed', NULL),
	(3, 'reopened', NULL);


-- required for "issue" code to work 
INSERT INTO `elixir_issuetype` (`id`, `type`, `description`, `weight`, `attribute`, `field_name`, `field_value`)
VALUES
	(1, 'invalid_url', NULL, NULL, 'link', 'url', NULL),
	(2, 'invalid_url', NULL, NULL, 'homepage', '', NULL),
	(3, 'invalid_url', NULL, NULL, 'download', 'url', NULL),
	(4, 'invalid_url', NULL, NULL, 'documentation', 'url', NULL),
	(5, 'invalid_url', NULL, NULL, 'credit', 'url', NULL),
	(6, 'invalid_url', NULL, NULL, 'contact', 'url', NULL),
	(7, 'missing', NULL, NULL, 'publication', 'id', NULL),
	(8, 'missing', NULL, NULL, 'documentation', 'type', 'terms_of_use'),
	(9, 'none', NULL, NULL, 'publication', 'id', NULL),
	(10, 'missing', NULL, NULL, 'license', NULL, NULL),
	(11, 'missing', NULL, NULL, 'contact', NULL, NULL),
	(12, 'ontology', NULL, NULL, 'topic', NULL, 'Topic'),
	(13, 'ontology', NULL, NULL, 'operation', NULL, 'Operation'),
	(14, 'ontology', NULL, NULL, 'data', NULL, 'Data'),
	(15, 'ontology', NULL, NULL, 'format', NULL, 'Format'),
	(16, 'ontology', NULL, NULL, 'topic', NULL, NULL),
	(17, 'ontology', NULL, NULL, 'operation', NULL, NULL),
	(18, 'ontology', NULL, NULL, 'data', NULL, NULL),
	(19, 'ontology', NULL, NULL, 'format', NULL, NULL),
	(20, 'ontology', NULL, NULL, 'topic', NULL, 'obsolete'),
	(21, 'ontology', NULL, NULL, 'operation', NULL, 'obsolete'),
	(22, 'ontology', NULL, NULL, 'data', NULL, 'obsolete'),
	(23, 'ontology', NULL, NULL, 'format', NULL, 'obsolete'),
	(24, 'ontology', NULL, NULL, 'topic', NULL, 'not_found'),
	(25, 'ontology', NULL, NULL, 'operation', NULL, 'not_found'),
	(26, 'ontology', NULL, NULL, 'data', NULL, 'not_found'),
	(27, 'ontology', NULL, NULL, 'format', NULL, 'not_found');
