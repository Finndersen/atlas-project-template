data "external_schema" "sqlalchemy" {
  program = [
    "python3",
    "scripts/load_models.py"
  ]
}

env "project_config" {
  src = data.external_schema.sqlalchemy.url
  dev = "docker://postgres/15/dev?search_path=public"
  migration {
    dir = "file://src/db/migrations"
  }
  format {
    migrate {
      diff = "{{ sql . \"  \" }}"
    }
  }
  diff {
    // Set indexes to be managed concurrently as this is not default behaviour
    concurrent_index {
      add  = true
      drop = true
    }
  }
}

lint {
	naming {
		match   = "^[a-z_]+$"
		message = "must be lowercase"
		error 	= true
	}
  # Should be reviewed on a case-by-case basis
	destructive {
    error   = false
  }
}
