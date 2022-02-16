INSTDIR=/var/www/uwsgi

deploy:
	install rsstoical.py $(INSTDIR)

restart:
	sudo systemctl restart uwsgi nginx
