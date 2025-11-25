<?php

class NotaFiscal {
    private $db;
    private static $ultimo_numero = 0;

    public function __construct() {
        $this->db = Database::getInstance();
    }

    /**
     * Gera número sequencial de nota fiscal
     */
    public function gerarNumeroNF() {
        try {
            $result = $this->db->query("SELECT COALESCE(MAX(CAST(SUBSTRING(numero_nf, 4) AS UNSIGNED)), 0) + 1 as proximo FROM Nota_fiscal");
            $row = $result->fetch();
            $numero = str_pad($row['proximo'], 6, '0', STR_PAD_LEFT);
            return "NF-$numero";
        } catch (Exception $e) {
            return "NF-000001";
        }
    }

    /**
     * Registra nova nota fiscal
     */
    public function criar($id_venda, $valor_total, $status = 'Emitida') {
        try {
            $numero_nf = $this->gerarNumeroNF();
            
            $stmt = $this->db->prepare("
                INSERT INTO Nota_fiscal (numero_nf, id_venda, valor_total, status, data_emissao)
                VALUES (?, ?, ?, ?, NOW())
            ");
            
            $stmt->execute([$numero_nf, $id_venda, $valor_total, $status]);
            $id = $this->db->lastInsertId();
            return ['id' => $id, 'numero_nf' => $numero_nf];
            
        } catch (Exception $e) {
            throw new Exception("Erro ao criar nota fiscal: " . $e->getMessage());
        }
    }

    /**
     * Recupera nota fiscal por ID
     */
    public function obterPorId($id) {
        try {
            $stmt = $this->db->prepare("
                SELECT * FROM Nota_fiscal 
                WHERE id = ?
            ");
            return $stmt->execute([$id])->fetchOne();
        } catch (Exception $e) {
            throw new Exception("Erro ao obter nota fiscal: " . $e->getMessage());
        }
    }

    /**
     * Recupera nota fiscal por número
     */
    public function obterPorNumero($numero_nf) {
        try {
            $stmt = $this->db->prepare("
                SELECT * FROM Nota_fiscal 
                WHERE numero_nf = ?
            ");
            return $stmt->execute([$numero_nf])->fetchOne();
        } catch (Exception $e) {
            throw new Exception("Erro ao obter nota fiscal: " . $e->getMessage());
        }
    }

    /**
     * Lista todas as notas fiscais
     */
    public function listar($filtros = []) {
        try {
            $sql = "SELECT * FROM Nota_fiscal WHERE 1=1";
            $params = [];

            if (!empty($filtros['data_inicio'])) {
                $sql .= " AND data_emissao >= ?";
                $params[] = $filtros['data_inicio'] . " 00:00:00";
            }

            if (!empty($filtros['data_fim'])) {
                $sql .= " AND data_emissao <= ?";
                $params[] = $filtros['data_fim'] . " 23:59:59";
            }

            if (!empty($filtros['status'])) {
                $sql .= " AND status = ?";
                $params[] = $filtros['status'];
            }

            if (!empty($filtros['numero_nf'])) {
                $sql .= " AND numero_nf LIKE ?";
                $params[] = "%" . $filtros['numero_nf'] . "%";
            }

            $sql .= " ORDER BY data_emissao DESC";

            $stmt = $this->db->prepare($sql);
            return $stmt->execute($params)->fetchAll();
        } catch (Exception $e) {
            throw new Exception("Erro ao listar notas fiscais: " . $e->getMessage());
        }
    }

    /**
     * Atualiza status da nota fiscal
     */
    public function atualizarStatus($id, $novo_status) {
        try {
            $stmt = $this->db->prepare("
                UPDATE Nota_fiscal 
                SET status = ?
                WHERE id = ?
            ");
            $stmt->execute([$novo_status, $id]);
            return $this->obterPorId($id);
        } catch (Exception $e) {
            throw new Exception("Erro ao atualizar status: " . $e->getMessage());
        }
    }

    /**
     * Exclui nota fiscal (apenas se não emitida)
     */
    public function deletar($id) {
        try {
            $nf = $this->obterPorId($id);
            if ($nf['status'] !== 'Rascunho') {
                throw new Exception("Apenas notas em rascunho podem ser excluídas");
            }

            $stmt = $this->db->prepare("
                DELETE FROM Nota_fiscal 
                WHERE id = ?
            ");
            return $stmt->execute([$id]) > 0;
        } catch (Exception $e) {
            throw new Exception("Erro ao excluir nota fiscal: " . $e->getMessage());
        }
    }

    /**
     * Obtém estatísticas de notas fiscais
     */
    public function obterEstatisticas($data_inicio = null, $data_fim = null) {
        try {
            $sql = "
                SELECT 
                    COUNT(*) as total_nfs,
                    SUM(valor_total) as valor_total,
                    COUNT(CASE WHEN status = 'Emitida' THEN 1 END) as nfs_emitidas,
                    COUNT(CASE WHEN status = 'Cancelada' THEN 1 END) as nfs_canceladas
                FROM Nota_fiscal 
                WHERE 1=1
            ";
            $params = [];

            if ($data_inicio) {
                $sql .= " AND data_emissao >= ?";
                $params[] = $data_inicio . " 00:00:00";
            }

            if ($data_fim) {
                $sql .= " AND data_emissao <= ?";
                $params[] = $data_fim . " 23:59:59";
            }

            $stmt = $this->db->prepare($sql);
            return $stmt->execute($params)->fetchOne();
        } catch (Exception $e) {
            throw new Exception("Erro ao obter estatísticas: " . $e->getMessage());
        }
    }

    /**
     * Verifica se número NF já existe
     */
    public function existeNumero($numero_nf) {
        try {
            $stmt = $this->db->prepare("
                SELECT COUNT(*) as total FROM Nota_fiscal 
                WHERE numero_nf = ?
            ");
            $result = $stmt->execute([$numero_nf])->fetchOne();
            return $result['total'] > 0;
        } catch (Exception $e) {
            return false;
        }
    }
}
