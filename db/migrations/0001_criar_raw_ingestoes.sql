-- Migração 0001 — tabela de log de coletas RAW (ADR 0004)
--
-- Registra metadados de cada execução dos motores de ingestão
-- (pipelines/ingestao/) — não armazena o dado bruto em si (isso vai para o
-- Supabase Storage, bucket "raw"), apenas o rastro de quando/o quê/onde.

create table if not exists raw_ingestoes (
    id bigint generated always as identity primary key,
    fonte text not null,
    indicador text,
    script text not null,
    coletado_em timestamptz not null default now(),
    storage_path text,
    tamanho_bytes bigint,
    sha256 text,
    status text not null check (status in ('sucesso', 'erro')),
    mensagem_erro text,
    metadata jsonb
);

create index if not exists idx_raw_ingestoes_fonte
    on raw_ingestoes (fonte, coletado_em desc);

alter table raw_ingestoes enable row level security;

-- Nenhuma policy para anon/authenticated: por padrão, ninguém além do
-- service_role (que ignora RLS) acessa esta tabela. Se no futuro a
-- plataforma precisar expor esses metadados publicamente (ex. "última
-- atualização" num painel), criar uma policy explícita de SELECT aqui.
