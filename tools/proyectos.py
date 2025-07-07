import requests
from agents import function_tool


@function_tool
def get_future_promotions() -> str:
    """
    Obtiene las promociones futuras de la asesora.
    """
    response = requests.get("https://unicohomes.com/nuestros_proyectos_proximos.php", verify=False)
    if response.status_code == 200:
        return response.text
    return "Error al obtener las promociones futuras."


@function_tool
def get_current_promotions() -> str:
    """
    Obtiene las promociones actuales de la asesora.
    """
    response = requests.get("https://unicohomes.com/nuestros_proyectos_venta.php", verify=False)
    if response.status_code == 200:
        return response.text
    return "Error al obtener las promociones actuales."

@function_tool
def get_past_promotions() -> str:
    """
    Obtiene las promociones pasadas de la asesora.
    """
    response = requests.get("https://unicohomes.com/nuestros_proyectos_promocion.php", verify=False)
    if response.status_code == 200:
        return response.text
    return "Error al obtener las promociones pasadas."

@function_tool
def get_information_for_specific_promotion_url(url: str) -> str:
    """
    Obtiene la información de una promoción específica.
    """
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        return response.text
    return "Error al obtener la información de la promoción."

