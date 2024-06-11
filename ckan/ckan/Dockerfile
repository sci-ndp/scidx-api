
FROM ckan/ckan-base:2.10.3

# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples
## Harvester ###
RUN pip3 install -e 'git+https://github.com/ckan/ckanext-harvest.git@master#egg=ckanext-harvest' && \
   pip3 install -r ${APP_DIR}/src/ckanext-harvest/pip-requirements.txt && \
   pip3 install -e 'git+https://github.com/ckan/ckanext-dcat.git#egg=ckanext-dcat' && \
   pip3 install -r ${APP_DIR}/src/ckanext-dcat/requirements.txt && \
   pip3 install ckanext-keycloak && \
   pip3 install python-keycloak-client==0.1.3\
   pip install ckanext-geoview

# will also require gather_consumer and fetch_consumer processes running (please see https://github.com/ckan/ckanext-harvest)

# Copy custom initialization scripts
COPY docker-entrypoint.d/* /docker-entrypoint.d/

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
COPY patches ${APP_DIR}/patches

RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done