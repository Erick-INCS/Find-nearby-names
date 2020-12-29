const { devConf, productionConf } = require("./credentials");
const mysql = require("mysql");
const fs = require('fs')

let ids = JSON.parse(fs.readFileSync('./ck_ids.json'));

// variable de conexion
let con = () => mysql.createConnection(devConf);

// funcion asincrona que realiza la conexion y ejecuta una consulta devolviendo el valor de la misma
function query(query, errRequest) {
    return new Promise((resolve, reject) => {
        let conn = con();

        // se conecta a la bd
        conn.connect(function(err) {
            if (err) {
                console.error("\r\n\r\nError al conectar con la BD\n\r");
                // console.error('err' + '\r\n')
                if (errRequest) {
                    defError(errRequest)(err);
                } else {
                    reject(err);
                }
            }
            // realiza la consulta
            conn.query(query, function(err, result, fields) {
                if (err) reject(err);

                resolve(result); //retorna el resultado
            });

            closeConn(conn); // cierra la conexion
        });
    });
}

// funcion que cierra la conexion
function closeConn(conn) {
    conn.end((err) => {
        if (err) console.error("Close connection -> " + err + "\r\n");
    });
}

async function insert(data) {
    data.forEach(elm => {
        console.log(`call reemplazar_empresa('${elm.delete}', '${elm.remains}');`);
    });
}

insert(ids);

// fs.writeFileSync('reemplazar_empresas.sql', sqlt);