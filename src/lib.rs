//! Python bindings for the Gum markup language parser.
//!
//! This module wraps the Rust core engine using PyO3, providing a native
//! Python extension for parsing, validating, and formatting Gum documents.

use gum_core::{parse, validate, format};
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use serde_json;

/// Parse a Gum document from a string.
///
/// Args:
///     input: The Gum document string to parse.
///
/// Returns:
///     A dictionary representing the parsed AST.
///
/// Raises:
///     ValueError: If the input is malformed.
#[pyfunction]
fn parse_gum(input: &str) -> PyResult<String> {
    let doc = parse(input).map_err(|e| PyValueError::new_err(e.to_string()))?;
    serde_json::to_string(&doc).map_err(|e| PyValueError::new_err(format!("Serialization error: {}", e)))
}

/// Validate a Gum document string.
///
/// Args:
///     input: The Gum document string to validate.
///
/// Returns:
///     A list of validation error strings (empty if valid).
///
/// Raises:
///     ValueError: If the input cannot be parsed.
#[pyfunction]
fn validate_gum(input: &str) -> PyResult<String> {
    let doc = parse(input).map_err(|e| PyValueError::new_err(e.to_string()))?;
    let errors = validate(&doc);
    serde_json::to_string(&errors).map_err(|e| PyValueError::new_err(format!("Serialization error: {}", e)))
}

/// Format a Gum document string.
///
/// Args:
///     input: The Gum document string to format.
///
/// Returns:
///     The formatted Gum document string.
///
/// Raises:
///     ValueError: If the input cannot be parsed.
#[pyfunction]
fn format_gum(input: &str) -> PyResult<String> {
    let doc = parse(input).map_err(|e| PyValueError::new_err(e.to_string()))?;
    Ok(format(&doc))
}

/// A Python module for parsing Gum markup language documents.
#[pymodule]
fn gum_parser(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_gum, m)?)?;
    m.add_function(wrap_pyfunction!(validate_gum, m)?)?;
    m.add_function(wrap_pyfunction!(format_gum, m)?)?;
    Ok(())
}
