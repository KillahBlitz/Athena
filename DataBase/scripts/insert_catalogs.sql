
BEGIN;

INSERT INTO public.tipos_riasec (riasec_id, tipo_riasec)
VALUES
    (0, 'Principal'),
    (1, 'Realista'),
    (2, 'Investigador'),
    (3, 'Artistica'),
    (4, 'Social'),
    (5, 'Emprendedor'),
    (6, 'Convencional');

INSERT INTO public.tipos_criterio (type_id, desc_criterio)

VALUES
    (1, 'PERFILES'),
    (2, 'PRINCIPAL');
COMMIT;
