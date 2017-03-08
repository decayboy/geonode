CREATE SEQUENCE public.test_fid_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE public.test_fid_seq
  OWNER TO geonode;

CREATE TABLE public.test
(
  fid integer NOT NULL DEFAULT nextval('test_fid_seq'::regclass),
  the_geom geometry(MultiPolygon,4326),
  risk_analysis character varying(80),
  hazard_type character varying(30),
  admin character varying(150),
  adm_code character varying(30),
  region character varying(80),
  CONSTRAINT test_pkey PRIMARY KEY (fid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.test
  OWNER TO geonode;

CREATE INDEX spatial_test_the_geom
  ON public.test
  USING gist
  (the_geom);

CREATE INDEX test_idx_nulls_low
  ON public.test (risk_analysis NULLS FIRST, hazard_type, adm_code, region);

--

CREATE SEQUENCE public.dimension_fid_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE public.dimension_fid_seq
  OWNER TO geonode;

CREATE TABLE public.dimension
(
  dim_id integer NOT NULL DEFAULT nextval('dimension_fid_seq'::regclass),
  dim_col character varying(30),
  dim_value character varying(255),
  CONSTRAINT dimension_pkey PRIMARY KEY (dim_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.dimension
  OWNER TO geonode;

CREATE INDEX dimension_idx
  ON public.dimension (dim_col, dim_value);

--

CREATE TABLE public.test_dimensions
(
  test_fid integer,
  dim1_id integer,
  dim2_id integer,
  dim3_id integer,
  dim4_id integer,
  dim5_id integer,
  value character varying(255),
  CONSTRAINT test_dimensions_dim1_id_fkey FOREIGN KEY (dim1_id)
      REFERENCES public.dimension (dim_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT test_dimensions_dim2_id_fkey FOREIGN KEY (dim2_id)
      REFERENCES public.dimension (dim_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT test_dimensions_dim3_id_fkey FOREIGN KEY (dim3_id)
      REFERENCES public.dimension (dim_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT test_dimensions_dim4_id_fkey FOREIGN KEY (dim4_id)
      REFERENCES public.dimension (dim_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT test_dimensions_dim5_id_fkey FOREIGN KEY (dim5_id)
      REFERENCES public.dimension (dim_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT test_dimensions_test_fid_fkey FOREIGN KEY (test_fid)
      REFERENCES public.test (fid) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT test_dimensions_unique_constraint UNIQUE (test_fid, dim1_id, dim2_id, dim3_id, dim4_id, dim5_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.test_dimensions
  OWNER TO geonode;
