/*
 * Cell preloader for kAFS filesystem.
 *
 * Copyright (C) David Howells (dhowells@redhat.com) 2018
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <syslog.h>
#include <errno.h>
#include <fcntl.h>
#include <getopt.h>
#include <arpa/inet.h>
#include <kafs/profile.h>
#include <kafs/cellserv.h>

static void verbose(const char *fmt, ...)
{
	va_list va;

	va_start(va, fmt);
	vprintf(fmt, va);
	putchar('\n');
	va_end(va);
}

/*
 * Just print an error to stderr or the syslog
 */
static void _error(const char *fmt, ...)
{
	va_list va;

	va_start(va, fmt);
	if (isatty(2)) {
		vfprintf(stderr, fmt, va);
		fputc('\n', stderr);
	} else {
		vsyslog(LOG_ERR, fmt, va);
	}
	va_end(va);
}

/*
 * Parse the cell database file
 */
int do_preload(const struct kafs_cell_db *db, bool redirect_to_stdout)
{
	unsigned int i;
	char buf[4096];
	int fd;

	if (!redirect_to_stdout) {
		fd = open("/proc/fs/afs/cells", O_WRONLY);
		if (fd == -1) {
			_error("Can't open /proc/fs/afs/cells: %m");
			exit(1);
		}
	} else {
		fd = 1;
	}

	for (i = 0; i < db->nr_cells; i++) {
		const struct kafs_cell *cell = db->cells[i];
		int n;

		n = snprintf(buf, sizeof(buf) - 1, "add %s", cell->name);
		if (write(fd, buf, n) != n) {
			if (errno != EEXIST) {
				_error("Can't add cell '%s': %m", cell->name);
				exit(1);
			}

			verbose("%s: Already exists", cell->name);
		}
		if (redirect_to_stdout)
			if (write(1, "\n", 1) == -1)
				perror("stdout");
	}

	if (!redirect_to_stdout) {
		if (close(fd) == -1) {
			_error("Can't close /proc/fs/afs/cells: %m");
			exit(1);
		}
	}

	exit(0);
}

static __attribute__((noreturn))
void usage(const char *prog)
{
	fprintf(stderr, "Usage: %s [-Dv] [<dbfile>*]\n", prog);
	exit(2);
}

int main(int argc, char *argv[])
{
	struct kafs_report report = {};
	const char *const *files;
	bool redirect_to_stdout = false;
	int opt;

	if (argc > 1 && strcmp(argv[1], "--help") == 0)
		usage(argv[0]);

	while (opt = getopt(argc, argv, "Dv"),
	       opt != -1) {
		switch (opt) {
		case 'D':
			redirect_to_stdout = true;
			break;
		case 'v':
			if (!report.verbose)
				report.verbose = verbose;
			else
				report.verbose2 = verbose;
			break;
		default:
			usage(argv[0]);
			break;
		}
	}

	argc -= optind;
	argv += optind;

	files = NULL;
	if (argc > 0)
		files = (const char **)argv;

	if (kafs_init_celldb(files, &report) < 0)
		exit(3);

	do_preload(kafs_cellserv_db, redirect_to_stdout);
	return 0;
}
