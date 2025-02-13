# PgManage 1.2.1 Bugfix Release

## Release Date: Feb 13 2024

## Release Notes
    
  - Bugs fixed:
    - fixed error notification link colors, added minor layout tweaks
    - fixed DB object tree node data refresh in some edge-cases
    - fixed erroneous "Discard Changes" warning when closing Query tab
    - fixed connectivity issues in built-in SSH terminal
    - fixed bug with multiple tabs highlighted as "active" #570
    - fixed app crash when schema editor is opened immediately after DB workspace is loaded
    - fixed bug with DROP database unable to complete in some cases #582
    - fixed bug with DB object tree context menu disappearing when monitoring dashboard refreshes #607
    - fixed race condition in Backup/Restore job status modal when running multiple jobs simultaneusly
    - fixed bug that allowed to register duplicate hotkey actions #611
    - fixed bug that caused old SQLite3 DB file being used when connection properties updated with a new file #598
    - fixed SQLite3 tables not ordered by name in DB object tree  # #596
    
  - Other changes:
    - bumped happy-dom version to fix potential security vulnerability in dev environment
    - silenced SASS deprecation warnings during js bundle build
    - plus icons are now used for all context menus associated with "create" action #557
    - improved readability of multiple modal windows shown on-top of each other
    - improved SQLite3 DB connection "Test"
    - improved database metadata loading and autocomplete engine initialization


# PgManage 1.2 Release

## Release Date: Nov 07 2024

## Release Notes

  - New features:
    - implemented support for adding/changing table indexes in Schema Editor
    - implemented Postgres role editor
    - added SQL error annotations in query editor
    - significant code completion improvements: added context-aware schema, table, view, column and function completions
    - added support for Postgres byte array display query results data grid
    
  - Bugs fixed:
    - fixes a bug in connection manager where "Discard changes" confirmation was shown after clicking "Test Connection" button
    - fixed a bug when PgManage was trying to restore tabs for closed DB workspaces
    - fixed a bug when "Discard changes" confirmation appeared after running "Explain/Analyze" and then closing DB workspace
    - fall back to unencrypted ssh key when no password is provided (thanks @El-Virus)
    - use user-provided database password instead of previously stored one when "Test connection" is clicked in connection manager
    - fixed a bug when backup/restore background job info was potentially accessible by other pgmanage user accounts
    - fixed a bug when redundant database back-end was instantiated when requesting database auto-completion metadata 
    - fixed a rare race condition when opening new database workspace
    - rearranged parts of DROP INDEX query template to make it runnable without needing extra modifications by the user
    - fixed a bug in Monitoring Dashboard when "Refresh all widgets" button was doing nothing after deleting all and restoring some monitoring widgets
    - fixes a bug in connection manager where "Discard changes" confirmation was shown for connections with passwords auto-filled by the browser
    - fixes a bug in schema editor where "DEFAULT" part of column definition was rendered regardless of presence of column default value
    
  - UI/UX Improvements:
    - new application startup screen
    - improved naming for exported CSV/XLS files
    
  - Other changes
    - Django updated from 4.2.11 to 4.2.16
    - cryptography updated from 36.0.2 to 41.0.7
    - pymysql updated from 1.0.x to 1.1.1
    - psycopg2 updated from 2.9.5 to 2.9.9
    - oracledb updated form 1.3.1 to 2.2.1
    - other occurrences of highlighed selection in query editor are now case-insensitive
    - implemented custom SESSION_SERIALIZER for improved sesion handling security
    - eager-load QueryTab components when opening database workspace for improved app responsiveness
    - added uniqueness validation to connection group names
    - removed unnecessary files from windows build of PgManage
    - changed default value for CSV separator setting
    - improved database back-end cleanup when no keep-alive requests come from the front-end
    - don't show error toast when running Explain/Analyze if PEV2 can display these errors by itself

# PgManage 1.1.1 Release

## Release Date: Sep 04 2024

## Release Notes

  - New features:
    - added IPv6 support for database connections
    - allow using UNIX domain socket paths in connection form -> server field (#438)
    - allow empty server values in the connection form for Postgres connections
    - password prompt will now be shown when user tries to establish database connection with wrong password
    - queries in console query history modal can now be copied to query tab with a double-click
    - console history buffer is now cleared from memory when "clear console" button is clicked

  - Bugs fixed:
    - fixed unrestricted code execution vulnerability in monitoring widget back-end. The issue was reported by Andrew Effenhauser, Ayman Hammad and Daniel Crowley of X-Force Red
    - fixed Entity Relationship not rendering diagram for some database layouts
    - fixes issue when expanded DB object tree node was not always scrolled to the top of viewport
    - fixed missing GRANT statements when roles is displayed in DDL tab
    - fixed a bug when application tabs may become unresponsive some cases
    - various minor layout fixes and tweaks


# PgManage 1.1 Release

## Release Date: Jul 16 2024

## Release Notes

 - New features:
   - pgmanage now uses database-specific syntax highlighting rules in SQL editors depending on the database type
   - added support for displaying column data types in query results data grid
   - columns in query results data grid can now be minimized/maximized by double-clicking the column header
   - switchable data grid layouts in query tabs: adaptive, compact and fit-content can be selected by clicking the ellipsis icon on the top-left corner of the grid
   - existing DB connection can now be cloned in connection manager dialog
   - the size of the next loaded data chunk can now be selcted when using "fetch-more" feature for large query results
   - added multi-statement queries support for SQlite3
   - database connections can now have a color label to make it easier to differentiate between different environments
   - scram-sha256 password hashing is now used when changing Postgres role passwords

 - Major Bugs fixed:
   - fixed documentation urls in Postgres DB object tree context menus
   - disable connection test button when test is in progress
   - fixed 'fetch all records' feature when running queries on non-postgres databases
   - fixed reversed DB object tree node ordering for inherited tables, foreign tables, sequences views, materialized views, trigger functions, event triggers, procedures, aggregates, types, fdw and tablespaces
   - fixed incorrect count of table partitions displayed in DB object tree when tree is refreshed
   - fixed Postgres unique indexes not being displayed in DDL tab
   - fixed live theme switching issues for some modal dialogs
   - improved escaping of HTML characters in data grid cells to prevent potential XSS
   - fixes issue when query execution timer may not be stopped when user cancels the query
   - fixed data saving issues in table data editor when using a database other than the one specified in DB connection properties (databases other than Postgres were affected)
   - fixed data editor issues when user tried to apply multiple row changes at once on SQlite3
   - improved back-end query thread termination when long-running query is cancelled by the user
   - fixed long polling request clean-up when user closes application tabs
   - fixed memory leak when working with DB console or SSH terminals
   - fixed updating last used date for SSH connections
   - fixed intermittent pgmanage startup issues on Windows platform
   - fixed query results data export when query contains explain or explain analyze keywords

 - UI/UX Improvements:
   - 'fetch all records' is now also supported DB console tabs
   - removed unnecessary schema name prefixes from table partition names in DB object tree
   - added warning about unsaved changes in Postgres Seever configuration tab before close
   - added confirmation when deleting configuration change histore records in Postgres Server configuration tab
   - added support for showing newline characters in query results data grid cells
   - added support for showing null and blank values in query results data grid cells
   - data grid is no longer hidden for queries that return 0 rows
   - added visual hints for column resize handles in data grid headers
   - improved DB console and SSH terminal performance when displaying large amounts of text
   - significantly improved performance of query result data grids when working with large amounts of data
   - it is now possible to reuse a query from the history dialog by double clicking on the correspoding query cell

 - Other changes
   - sshtunnel bumped from 0.1.5 to 0.4.0
   - optimized front-end imports to reduce js bundle size
   - optimized peformance of several back-end queries
   - project migrated from bootstrap 4 to bootstrap 5
   - pev2 bumped from 1.8 to 1.11
   - legacy code clean-up
   - removed support for EOL Postgres versions
   - added support for creating debug .appimage builds
   - added support for masking sensitive data in error logs
   - project migrated from django 3.2 to django 4.2
   - bumped xterm.js from 5.2 to 5.5


# PgManage 1.0.1 Bugfix Release

## Release Date: May 16 2024

## Release Notes

  - Bugs fixed:
   - trim explain/explain analyze prefix of the query when "explain" or "explain analyze" button is clicked
   - disable unnecessary row selection in command/query history data grid
   - fix cell data viewer modal working incorrectly when the cell contains numeric valueis Number
   - clean-up backup/restore job status polling when corresponding backup/restore tab is closed
   - make DB object tree resize line easier to grab when scrollbar is also present in DB object tree
   - fixed query results data-grid autosizing
   - fixed fetch more/fetch all records for SQLite3
   - disable drag-n-drop of DB session tabs above Connections/Welcome/Snippets sidebar items
   - don't hide connection/group form in connections dialog after connection/group is saved
   - add confirmation for connection group deletion
   - don't show the "unsaved changes" popup when user saved the new connection group and tries to select other group/connection


# PgManage 1.0 Release

## Release Date: Apr 17 2024

## Release Notes

 - New features:
   - added SQL file import into Query and Snippet tabs
   - added SQL file export from Query and Snippet tabs
   - query tab title now displays the name of the imported file
   - query history can now be filtered by database
   - added MySQL and MariaDB support in database Schema editor
   - new autocomplete in SQL code editor
   - added search and replace in SQL code editor
   - added live query execution timer for long-running queries
   - make "restore application tabs" behavior configurable in application settings
   - make DB object tree "scroll into view" behavior configurable in application settings

 - Major Bugs fixed:
   - fixed database tab restore concurrency issues when restoring multiple workspaces
   - change selected database when database child nodes are clicked
   - update workspace tooltips when corresponding connection gets renamed
   - don't try to run explain/analyze visualizer for non-Postgres database connections
   - don't allow setting nullable and primary-key column properties on schema editor
   - fixed various layout isues in UI walkthrough component
   - fixed issue when new monitoring widget modal wasn't possible to open after widget save/update
   - fixed automatic selection of last used database when reconnecting
   - reset connection properties form when connection manager dialog is closed

 - UI/UX Improvements:
   - improved application font size change handling various parts of the app
   - copy only selected text into clipboard if editor has a selection
   - application tabs now fit within a single row and can be scrolled if there are too many tabs
   - improved UI performance during application panel resize
   - improved UI responsiveness when application window is resized
   - application data grids layout improvements
   - data editor cell contents modal can now be shown by double-clicking the cell
   - database query tabs now show the associated database in tab title
   - added buttons for database tab scrolling
   - improved displaying of long error messages in application toast notifications
   - warn user about unsaved connection changes in connection manager dialog

 - Other changes
   - code indent feature now has a maximum content length limited to 75mb
   - monitoring dashboard was rewritten in Vuejs
   - application tab management code was rewritten in Vuejs
   - password dialogs were rewritten in Vuejs
   - improved SSH tunnel error handling
   - improved error reporting when SSH tunnel issues occur
   - legacy code cleaned-up/removed
   - improved database back-end clean-up when query is cancelled by the user
   - updated django from 3.2.18 to 3.2.25
   - updated tabulator.js  from 5.5.2 to 6.2
   - updated chart.js
   - significantly improved application error logging


# PgManage 1.0 RC 1

## Release Date: Jan 4 2024

## Release Notes

 - New features:
   - new welcome screen which displays app shortcuts and recent connections list
   - added "run selection" feature in query editor
   - autocomplete setting is now stored separately for each DB connection
   - added SQLite3 support in table editor

 - Major Bugs fixed:
   - various layout fixes on snippets panel
   - fixed memory leak in snippets panel tree view
   - fixed postgres binary path corruption when pigz binary path is changed in settings dialog
   - added snippet and snippet folder name validation
   - added CSV delimiter validation in app settings
   - multiple fixes in Getting Started wizard
   - fixed query editor re-focusing when autocomplete widget closes
   - added connection group name validation
   - fixed disabled DB connection string input when creating new connection

 - UI/UX Improvements:
   - slightly improved app startup speed

 - Other changes
   - improved error handling when app back-end is down or unavailable due to network issues
   - application data grids migrated from Handsontable to Tabulator.js
   - updated Vuejs and Bootstrap libraries


# PgManage 1.0 Beta 3

## Release Date: Nov 4 2023

## Release Notes

 - New features:
   - added UI for creating/altering DB tables (currently for Postgres only)
   - added new Entity Relationship Diagram for all supported databases
   - added PIGZ support for database backup and restore
   - added UI for PG Cron extension

 - Major Bugs fixed:
   - fixed the issue when "Test Connection" action fails on previously saved DB connection
   - fixed SQL autocomplete issues

 - UI/UX Improvements:
   - default TCP port in database connection form is now prepopulated based on selected database type
   - improved styling for Pev2 Query Explain component
   - major dark theme improvements
   - the data editor tab is rewritten in Vuejs with various UX improvements like revert changed, display number of changes made etc
   - the state of autocomplete toggle switch is now saved to application settings
   - in DB Query tab the Cancel Query button is now displayed for long running queries only (>1000ms)
   - various layout improvements on DB Query tab, application pane separators etc.
   - minimized UI visual clutter

 - Other changes
   - database object tree was fully rewritten in Vuejs
   - moved SQL formatting/indentation to front-end
   - refactored DB Object APIs
   - JS assets are now managed with NPM and bundled with Vite
   - Long-polling code cleaned up and refactored
   - DB console tab was fully rewritten in Vuejs
   - DB query tab was fully rewritten in Vuejs


# PgManage 1.0 Beta 2

## Release Date: Jun 15 2023

## Release Notes

 - New features:
   - ability to disable CSV header when exporting data grid contents
   - added UI for Postgres extension management
   - new hierarchical connections menu
   - use random TCP port number for the application back-end process so Pgmanage does not occupy ports commonly used by other applications
   - ability to select SSL connection options in Connection Management dialog
   - remember and restore application window position and size when the app starts
   - added configurable date/time display format in the application settings dialog
   - restore the last used database and query tabs when pgmanage starts

 - Major Bugs fixed:
   - if the query entered by the user contains explain keyword, clicking on explain/analyze button will no longer prepend the query with an extra explain keyword (previously this bug resulted in syntactically incorrect query)

 - UI/UX Improvements:
    - ability to work with multiple databases within a DB session without needing to select the "active" database
    - if query entered by the user contains explain keyword, the explain tab will be opened automatically when user clicks the "Run query" button
    - explain and analyze buttons are now grouped together and separated from other query buttons
    - pre-set database connection TCP port in the Connection Management dialog based on selected database type
    - add visually matching themes for query editor

 - Other changes
    - django has been updated from 2.2 to 3.2
    - bundled python version changed from 3.8 to 3.9
    - code clean-up and refactoring
    - moved application shared data into globally accessible Pinia store
    - replace cx_Oracle library with oracledb

# PgManage 1.0 Beta

## Release Date: Apr 20 2023

## Release Notes

- New features:
  - added backup/restore support for Postgres
  - first version of PgManage Handbook was published to https://pgmanage.readthedocs.io/en/latest

- Major Bugs fixed:
  - fixed .AppImage compatibility issues for newer Linux distributions which do not have libcrypt installed
  - added logic to terminate stale back-end process if the front-end process crashes
  - fixed application UI process memory leaks


- UI/UX Improvements:
  - improved support for configuration options search in Postgres Server Configuration Management
  - automatically readjust query editor font size when the application font size changes
  - various application layout and UI improvements
  - limited minimum application window size to 1024x766
  - fixed splash screen flickering/position issues during the application startup
  - add PgManage Handbook links to application error modal dialogs
  - improved handling of drag-and-drop reordering for database operations tabs

- Other changes
  - added support for configurable Postgresql Client binary path in application settings
  - excluded SASS libraries and .sass files from the release builds
  - include EGL/GLES libraries into app release builds
  - pev2 upgraded to v1.7.0
  - removed "plugins" and other obsolete menu items from the application UI
  - removed unused files and dead code from the project
  - shred SSH keys stored in the app during the Master Password Reset

# PgManage 1.0 Alpha

## Release Date: Feb 21 2023

## Release Notes

- New features:
  - new connection management UI
  - added support for postgres server configuration management
  - new explain/analyze UI powered by pev2, including pev2 dark theme support
  - connection credential encryption
  - backported support for monitoring data-grid-based monitoring widgets
  - backported pie charts widgets for numbackends and database sizes
  - added password strength validation for user and master passwords
  - PostgreSQL 9.6, 10, 11, 12, 13, 14 and 15 support

- Major Bugs fixed:
  - fixed data export to csv/xls format in the desktop version of the app
  - added superuser permission check on all user management APIs
  - extra validations added to prevent creation of unnamed connection groups
  - fixed external links not working in the desktop variant of the app
  - fixed postgres special commands on postgresql versions 12 and higher
  - fixed broken postgres documentation links available in database tree view menus
  - made all web/cdn app dependencies local so pgmanage can work properly without an internet connection

- UI/UX Improvements:
  - reorganized connection management menus in the left menu bar
  - fixed DDL tab auto resizing
  - the top-right utilities menu now expands on click instead of mouse-hover
  - added DDL/properties tab resize limits to prevent it from becoming impossible to grab/resize back
  - unified tooltip appearance throughout the whole app
  - unified pictogram look and feel thoughout the whole app
  - improved database tree view navigation by adding smooth scroll to the newly expanded tree node. previously when some tree view node was expanded it jumped out of sight
  - improved data grid/table readability
  - improved database entity tree view readability
  - fixed date formatting in sql command history grid
  - fixed date formatting in db console command history grid
  - proper styling for dialog primary and secondary buttons. the secondary buttons in forms and dialogs were previously looked disable/grayed-out which was confusing.
  - the autocommit checkbox on query tab now stays visible despite of application window size
removed the option to make connections public in desktop variant of the app (which has only one user so shared/public connections make no sense)

- Other changes
  - added postgresql 14 and 15  support
  - application data directory and db/log file naming was changed from omnidb* to pgmanage*.
