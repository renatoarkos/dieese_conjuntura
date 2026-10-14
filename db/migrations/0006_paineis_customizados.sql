-- Migração 0006 — painéis customizados (montagem de dashboard com arrastar/
-- redimensionar, pedido do responsável do projeto em 2026-10-14: "uma
-- plataforma de interação... arrastar os gráficos dentro do quadro dando a
-- melhor dimensionalidade a cada um").
--
-- Guarda só o LAYOUT (quais indicadores, posição/tamanho de cada cartão no
-- grid, tipo de gráfico escolhido) — nunca o dado em si, que continua vindo
-- ao vivo de indicadores_serie a cada carregamento. Um painel customizado
-- "quebrado" por um indicador removido/renomeado não corrompe dado nenhum,
-- só deixa de mostrar aquele cartão.

create table if not exists paineis_customizados (
    id bigint generated always as identity primary key,
    usuario_id uuid not null references auth.users (id) on delete cascade,
    nome text not null default 'Meu painel',
    layout jsonb not null default '[]'::jsonb,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

create index if not exists idx_paineis_customizados_usuario
    on paineis_customizados (usuario_id);

alter table paineis_customizados enable row level security;

-- Cada pessoa só vê/edita os próprios painéis — nunca público, nunca
-- compartilhado entre contas (diferente de indicadores/indicadores_serie,
-- que são dado público; aqui é preferência pessoal de layout).
create policy "paineis_customizados: dono le"
    on paineis_customizados for select
    to authenticated
    using (usuario_id = auth.uid());

create policy "paineis_customizados: dono insere"
    on paineis_customizados for insert
    to authenticated
    with check (usuario_id = auth.uid());

create policy "paineis_customizados: dono atualiza"
    on paineis_customizados for update
    to authenticated
    using (usuario_id = auth.uid())
    with check (usuario_id = auth.uid());

create policy "paineis_customizados: dono apaga"
    on paineis_customizados for delete
    to authenticated
    using (usuario_id = auth.uid());
