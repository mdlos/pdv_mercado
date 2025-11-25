<?php
class Permissoes {
    private static $permissoes = [
        'Administrador' => [
            'vendas', 'estoque', 'compras', 'devolucoes', 'relatorios', 'funcionarios', 'configuracoes'
        ],
        'Gerente' => [
            'vendas', 'estoque', 'compras', 'devolucoes', 'relatorios', 'configuracoes'
        ],
        'Vendedor' => [
            'vendas', 'devolucoes'
        ],
        'Caixa' => [
            'vendas', 'devolucoes'
        ],
        'Estoquista' => [
            'estoque', 'compras'
        ]
    ];

    public static function tem($acao) {
        if (!isset($_SESSION['usuario'])) {
            return false;
        }
        $tipo = $_SESSION['usuario']['tipo_funcionario'];
        $perms = self::$permissoes[$tipo] ?? [];
        return in_array($acao, $perms);
    }

    public static function isAdmin() {
        return isset($_SESSION['usuario']) && $_SESSION['usuario']['tipo_funcionario'] === 'Administrador';
    }

    public static function isGerente() {
        return isset($_SESSION['usuario']) && $_SESSION['usuario']['tipo_funcionario'] === 'Gerente';
    }

    public static function exigir($acao) {
        if (!self::tem($acao)) {
            header('HTTP/1.1 403 Forbidden');
            die('Acesso negado');
        }
    }

    public static function listar() {
        if (!isset($_SESSION['usuario'])) {
            return [];
        }
        $tipo = $_SESSION['usuario']['tipo_funcionario'];
        return self::$permissoes[$tipo] ?? [];
    }
}
