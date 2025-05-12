import React from "react";

/* REACT-BOOTSTRAP */
import {Container, Row, Col} from "react-bootstrap";

function Footer() {
    return (
        <footer>
            <Container>
                <Row>
                    <Col className="text-center py-3">Copyright &copy; E-Commerce</Col>
                </Row>
            </Container>
        </footer>
    );
}

export default Footer;
