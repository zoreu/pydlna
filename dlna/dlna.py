from functools import partial
import threading
import selectors
import argparse
import os
import shutil
try:
  from dlna import getch
except:
  import getch
import subprocess
import time
from http import server, client, HTTPStatus
import socket
import socketserver
import ssl
import urllib.request, urllib.parse, urllib.error
from io import BytesIO
from xml.dom import minidom
import json
import html
import struct
import array
import hashlib
import base64
import re
import webbrowser
import mimetypes
import random
import locale
import ctypes

FR_STRINGS = {
  'mediaprovider': {
    'opening': 'Ouverture de "%s" reconnu comme "%s" en mode "%s" - titre: %s',
    'extension': 'Extension de "%s" retenue comme "%s"',
    'failure': 'Échec de l\'ouverture de "%s" en tant que "%s"',
    'subopening': 'Ouverture des sous-titres "%s" reconnus comme "%s"',
    'subextension': 'Extension des sous_titres retenue comme "%s"',
    'subfailure': 'Échec de l\'ouverture des sous-titres "%s" en tant que "%s"',
    'contentpath': 'chemin d\'accès de contenu',
    'contenturl': 'url de contenu',
    'webpageurl': 'url de page web',
    'loadstart': 'Début du chargement dans le tampon du contenu',
    'segmentbuffering': 'Segment %d -> placement dans la zone %d du tampon',
    'segmentfailure': 'Segment %d -> échec de lecture du contenu',
    'loadstop': 'Fin du chargement dans le tampon du contenu',
    'loadinterrupt': 'Interruption du chargement dans le tampon du contenu',
    'connection': 'Connexion pour diffusion de "%s": persistente = %s - requêtes partielles = %s',
    'yes': 'oui',
    'no': 'non',
    'indexation': 'Indexation du tampon sur la connexion %d',
    'deindexation': 'Désindexation du tampon',
    'translation': 'Translation du tampon vers la position %d',
    'present': 'Segment %d -> déjà présent dans la zone %d du tampon'
  },
  'mediaserver': {
    'connection': 'Connexion au serveur de diffusion de %s:%s',
    'deliverystart': 'Connexion %d -> début de la distribution du contenu à %s:%s',
    'delivery1': 'Connexion %d -> segment %d -> distribution à partir de la zone %d du tampon',
    'delivery2': 'Connexion %d -> segment %d -> distribution',
    'delivery3': 'Connexion %d -> segment %d -> distribution à partir du tampon',
    'exceeded': 'Connexion %d -> segment %d -> la zone %d a été dépassée par la queue du tampon',
    'expulsion': 'Connexion %d -> segment %d -> expulsion du tampon',
    'failure': 'Connexion %d -> segment %d -> échec de distribution du contenu',
    'deliveryfailure': 'Connexion %d -> échec de distribution du contenu',
    'deliverystop': 'Connexion %d -> fin de la distribution du contenu',
    'subdelivery': 'Distribution des sous-titres à %s:%s',
    'subfailure': 'Échec de distribution des sous-titres à %s:%s',
    'start': 'Démarrage, sur l\'interface %s, du serveur de diffusion en mode %s%s',
    'sequential': 'séquentiel',
    'random': 'aléatoire',
    'unsupported': ' non supporté par la source',
    'shutdown': 'Fermeture du serveur de diffusion'
  },
  'dlnanotification': {
    'start': 'Démarrage du serveur d\'écoute des notifications d\'événement de %s DLNA à l\'adresse %s:%s',
    'stop': 'Arrêt du serveur d\'écoute des notifications d\'événement de %s DLNA à l\'adresse %s:%s',
    'alreadyactivated': 'Serveur d\'écoute des notifications d\'événement de %s DLNA à l\'adresse %s:%s déjà activée',
    'receipt': 'DLNA Renderer %s -> service %s -> réception de la notification d\'événement %s',
    'notification': 'DLNA Renderer %s -> Service %s -> notification d\'événement %s -> %s est passé à %s',
    'alert': 'DLNA Renderer %s -> Service %s -> notification d\'événement %s -> alerte: %s est passé à %s'
  },
  'dlnaadvertisement': {
    'receipt': 'Réception, sur l\'interface %s, d\'une publicité du périphérique %s (%s:%s): %s',
    'ignored': 'Publicité du périphérique %s (%s:%s) ignorée en raison de la discordance d\'adresse de l\'URL de description',
    'set': 'Mise en place de l\'écoute des publicités de périphérique DLNA sur l\'interface %s',
    'fail': 'Échec de la mise en place de l\'écoute des publicités de périphérique DLNA sur l\'interface %s',
    'alreadyactivated': 'Écoute des publicités de périphérique DLNA déjà activée',
    'start': 'Démarrage du serveur d\'écoute des publicités de périphérique DLNA',
    'stop': 'Arrêt du serveur d\'écoute des publicités de périphérique DLNA'
  },
  'dlnahandler': {
    'ip_failure': 'Échec de la récupération de l\'adresse ip de l\'hôte',
    'registering': 'Enregistrement du %s %s sur l\'interface %s',
    'msearch1': 'Envoi d\'un message de recherche de uuid:%s',
    'msearch2': 'Envoi d\'un message de recherche de périphérique DLNA',
    'msearch3': 'Envoi d\'un message de recherche de %s DLNA',
    'sent': 'Envoi du message de recherche sur l\'interface %s',
    'fail': 'Échec de l\'envoi du message de recherche sur l\'interface %s',
    'receipt': 'Réception, sur l\'interface %s, d\'une réponse au message de recherche de %s:%s',
    'ignored': 'Réponse de %s:%s ignorée en raison de la discordance d\'adresse de l\'URL de description',
    'alreadyactivated': 'Recherche de %s DLNA déjà activée',
    'start': 'Démarrage de la recherche de %s DLNA',
    'stop': 'Fin de la recherche de %s DLNA',
    'commandabandonment': '%s %s -> service %s -> abandon de l\'envoi de la commande %s',
    'commandsending': '%s %s -> service %s -> envoi de la commande %s',
    'commandfailure': '%s %s -> service %s -> échec de l\'envoi de la commande %s',
    'commandsuccess': '%s %s -> service %s -> succès de l\'envoi de la commande %s',
    'responsefailure': '%s %s -> service %s -> échec du traitement de la réponse à la commande %s',
    'responsesuccess': '%s %s -> service %s -> succès de la réception de la réponse à la commande %s',
    'advertalreadyactivated': 'Écoute des publicités de %s déjà activée',
    'advertstart': 'Démarrage de l\'écoute des publicités de %s',
    'advertstop': 'Fin de l\'écoute des publicités de %s',
    'subscralreadyactivated': 'Renderer %s -> service %s -> souscription au serveur d\'événements déjà en place',
    'subscrfailure': 'Renderer %s -> service %s -> échec de la demande de souscription au serveur d\'événements',
    'subscrsuccess': 'Renderer %s -> service %s -> souscription au serveur d\'événements sous le SID %s pour une durée de %s',
    'subscrrenewfailure': 'Renderer %s -> service %s -> échec de la demande de renouvellement de souscription de SID %s au serveur d\'événements',
    'subscrrenewsuccess': 'Renderer %s -> service %s -> renouvellement de la souscription de SID %s au serveur d\'événements pour une durée de %s',
    'subscrunsubscrfailure': 'Renderer %s -> service %s -> échec de la demande de fin de souscription de SID %s au serveur d\'événements',
    'subscrunsubscrsuccess': 'Renderer %s -> service %s -> fin de la souscription de SID %s au serveur d\'événements'
  },
  'websocket': {
    'endacksuccess': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> succès de l\'envoi de l\'accusé de réception de l\'avis de fin de connexion',
    'endackfailure': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> échec de l\'envoi de l\'accusé de réception de l\'avis de fin de connexion',
    'errorendnotification': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> envoi d\'avis de fin de connexion pour cause d\'erreur %s',
    'errorendnotificationsuccess': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> succès de l\'envoi de l\'avis de fin de connexion',
    'errorendnotificationfailure': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> échec de l\'envoi de l\'avis de fin de connexion',
    'terminationdatasuccess': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> succès de l\'envoi de la donnée de terminaison %s',
    'terminationdatafailure': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> échec de l\'envoi de la donnée de terminaison %s',
    'endnotificationsuccess': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> succès de l\'envoi de l\'avis de fin de connexion',
    'endnotificationfailure': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> échec de l\'envoi de l\'avis de fin de connexion',
    'datasuccess': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> envoi de la donnée %s',
    'datafailure': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> échec de l\'envoi de la donnée %s',
    'datareceipt': 'WebSocket serveur %s:%s/%s -> WebSocket %s:%s -> réception de la donnée %s',
    'connectionrequest': 'WebSocket serveur %s:%s -> demande de connexion du WebSocket %s:%s',
    'connectionrequestinvalid': 'WebSocket serveur %s:%s -> demande de connexion du WebSocket %s:%s invalide',
    'connectionrequestnotfound': 'WebSocket serveur %s:%s -> chemin de demande de connexion du WebSocket %s:%s introuvable: /%s',
    'connectionresponsefailure': 'WebSocket serveur %s:%s/%s -> échec de l\'envoi de la réponse à la demande de connexion du WebSocket %s:%s',
    'connection': 'WebSocket serveur %s:%s/%s -> connexion au WebSocket %s:%s',
    'endack': 'WebSocket serveur %s:%s/%s -> accusé de réception de fin de connexion du WebSocket %s:%s',
    'endnotification': 'WebSocket serveur %s:%s/%s -> avis de fin de connexion du WebSocket %s:%s',
    'connectionend': 'WebSocket serveur %s:%s/%s -> fin de connexion au WebSocket %s:%s',
    'start': 'Démarrage du serveur pour Websocket à l\'adresse %s:%s',
    'fail': 'Échec du démarrage du serveur pour Websocket à l\'adresse %s:%s',
    'open': 'Websocket serveur %s:%s: ouverture du canal /%s',
    'close': 'Websocket serveur %s:%s: fermeture du canal /%s',
    'shutdown': 'Fermeture du serveur pour Websocket à l\'adresse %s:%s'
  },
  'webinterface': {
    'ip_failure': 'Échec de la récupération de l\'adresse ip de l\'hôte',
    'connection': 'Connexion de l\'interface web %s:%s',
    'response': 'Réponse à l\'interface Web %s:%s - requête: %s',
    'formdatareceipt': 'Réception de la donnée de formulaire %s de %s:%s',
    'formdatareject': 'Rejet de la donnée de formulaire %s de %s:%s',
    'playbackaccept': 'Prise en compte de la demande de lecture de %s%s à partir de %s sur %s de %s:%s',
    'playbacksub': ' et %s',
    'playbackreject': 'Rejet de la demande de lecture de %s%s à partir de %s sur %s de %s:%s',
    'rendererstart': 'Démarrage du gestionnaire d\'affichage de renderer pour serveur d\'interface Web',
    'launchrendererstart': 'Démarrage du gestionnaire d\'affichage de renderer dans le formulaire de lancement pour serveur d\'interface Web',
    'rendererstop': 'Arrêt du gestionnaire d\'affichage de renderer pour serveur d\'interface Web',
    'controlstart': 'Démarrage du gestionnaire de contrôleur de lecture pour serveur d\'interface Web',
    'controlinterrupt': 'Interruption du gestionnaire de contrôleur de lecture pour serveur d\'interface Web',
    'controlrenderer': 'Sélection du renderer %s sur l\'interface %s',
    'playlist': 'Liste de lecture générée depuis l\'adresse %s: %s contenus média',
    'nocontent': 'Absence de contenu média sous l\'adresse %s',
    'nonegapless': 'Absence de support de la lecture sans blanc par le renderer %s',
    'gapless': 'Lecture sans blanc des contenus média depuis l\'adresse %s activée',
    'nogapless': 'Adresse %s incompatible avec la lecture sans blanc',
    'norendereranswer': 'Absence de réponse du renderer %s',
    'ready': 'Prêt pour lecture de "%s"%s, par %s, sur le renderer "%s"',
    'subtitled': ', sous-titrée',
    'direct': 'transmission directe de l\'adresse',
    'random': 'diffusion via serveur en mode accès aléatoire',
    'sequential': 'diffusion via serveur en mode accès séquentiel%s',
    'remuxed': ', remuxé en %s',
    'controlstop': 'Arrêt du gestionnaire de contrôleur de lecture pour serveur d\'interface Web%s%s%s%s',
    'status': ' - statut ',
    'start': 'Démarrage du serveur d\'interface Web sur l\'interface %s',
    'alreadyrunning': 'Serveur d\'interface Web déjà en place',
    'fail': 'Échec du démarrage du serveur d\'interface Web sur l\'interface %s',
    'shutdown': 'Fermeture du serveur d\'interface Web',
    'jstart': 'Interface de démarrage',
    'jcontrol': 'Interface de contrôle',
    'jrenderers': 'Renderers',
    'jmwebsocketfailure': 'Échec de l\'établissement de la connexion WebSocket',
    'jmrenderersclosed': 'Renderers - interface close',
    'jmentervalidurl': 'Saisissez une URL de contenu média valide',
    'jmentervalidsuburl': 'Saisissez une URL de sous-titres valide',
    'jmselectrenderer': 'Sélectionnez d\'abord un renderer',
    'jplaybackposition': 'Position de lecture',
    'jgoplay': 'Lire',
    'jreset': 'Réinitialiser',
    'jplay': 'Lecture',
    'jpause': 'Pause',
    'jstop': 'Arrêt',
    'jinterfaceclosed': 'interface close',
    'jback': 'retour',
    'jinitialization': 'initialisation',
    'jready': 'prêt',
    'jreadyfromstart': 'prêt (lecture à partir du début)',
    'jinprogress': 'en cours',
    'jinplayback': 'lecture',
    'jinpause': 'pause',
    'jinstop': 'arrêt',
    'jplaylist': 'Liste de lecture',
    'jurl': 'URL du média',
    'jstatus': 'Statut',
    'jtargetposition': 'Position cible',
    'jmstop': 'Arrêter la lecture ?'
  },
  'parser': {
    'license': 'Ce programme est sous licence copyleft GNU GPLv3 (voir https://www.gnu.org/licenses)',
    'help': 'affichage du message d\'aide et interruption du script',
    'ip': 'adresse IP de l\'interface web [auto-sélectionnée par défaut - "0.0.0.0", soit toutes les interfaces, si option présente sans mention d\'adresse]',
    'port': 'port TCP de l\'interface web [8000 par défaut]',
    'hip': 'adresse IP du contrôleur/client DLNA [auto-sélectionnée par défaut - "0.0.0.0", soit toutes les interfaces, si option présente sans mention d\'adresse]',
    'rendereruuid': 'uuid du renderer [premier renderer sans sélection sur l\'uuid par défaut]',
    'renderername': 'nom du renderer [premier renderer sans sélection sur le nom par défaut]',
    'servertype': 'type de serveur (a:auto, s:séquentiel, r:aléatoire, g:sans-blanc/aléatoire, n:aucun) [a par défaut]',
    'buffersize': 'taille du tampon en blocs de 1 Mo [75 par défaut]',
    'bufferahead': 'taille du sous-tampon de chargement par anticipation en blocs de 1 Mo [25 par défaut]',
    'muxcontainer': 'type de conteneur de remuxage précédé de ! pour qu\'il soit systématique [MP4 par défaut]',
    'onreadyplay': 'lecture directe dès que le contenu média et le renderer sont prêts [désactivé par défaut]',
    'displayrenderers': 'Affiche les renderers présents sur le réseau',
    'start': 'Démarre l\'interface à partir de la page de lancement',
    'control': 'Démarre l\'interface à partir de la page de contrôle',
    'mediasrc1': 'adresse du contenu multimédia [aucune par défaut]',
    'mediasrc2': 'adresse du contenu multimédia',
    'mediasubsrc': 'adresse du contenu de sous-titres [aucun par défaut]',
    'mediasublang': 'langue de sous-titres, . pour pas de sélection [fr,fre,fra,fr.* par défaut]',
    'mediasublangcode': 'fr,fre,fra,fr.*',
    'mediastartfrom': 'position temporelle de démarrage ou durée d\'affichage au format H:MM:SS [début/indéfinie par défaut]',
    'slideshowduration': 'durée d\'affichage des images, si mediastrartfrom non défini, au format H:MM:SS [aucune par défaut]',
    'endless': 'lecture en boucle [désactivé par défaut, toujours actif en mode lecture aléatoire de liste]',
    'verbosity': 'niveau de verbosité de 0 à 2 [0 par défaut]',
    'stopkey': 'Appuyez sur "S" pour stopper',
    'auto': 'auto',
    'sequential': 'séquentiel',
    'random': 'aléatoire',
    'remuxkey': 'Appuyez sur "!" et "M" pour alterner entre les modes de remuxage (MP4, MPEGTS, !MP4, !MPEGTS) pour la prochaine session de lecture - mode actuel: %s',
    'servertypekey': 'Appuyez sur "T" pour alterner entre les types de serveur (auto, séquentiel, aléatoire) pour la prochaine session de lecture - mode actuel: %s',
    'endlesskey': 'Appuyez sur "E" pour activer/désactiver la lecture en boucle - mode actuel: %s',
    'enabled': 'activé',
    'disabled': 'désactivé',
    'remuxnext': 'Mode de remuxage pour la prochaine session de lecture: %s',
    'servertypenext': 'Type de serveur pour la prochaine session de lecture: %s',
    'endlessstatus': 'Lecture en boucle: %s'
  }
}
EN_STRINGS = {
  'mediaprovider': {
    'opening': 'Opening of "%s" recognized as "%s" in "%s" mode - title: %s',
    'extension': 'Extension of "%s" retained as "%s"',
    'failure': 'Failure of the opening of "%s" as "%s"',
    'subopening': 'Opening of the subtitles "%s" recognized as "%s"',
    'subextension': 'Extension of the subtitles retained as "%s"',
    'subfailure': 'Failure of the opening of the subtitles "%s" as "%s"',
    'contentpath': 'content path',
    'contenturl': 'content url',
    'webpageurl': 'web page url',
    'loadstart': 'Start of the loading in the content buffer',
    'segmentbuffering': 'Segment %d -> placement in the zone %d of the buffer',
    'segmentfailure': 'Segment %d -> failure of reading of the content',
    'loadstop': 'End of the loading in the content buffer',
    'loadinterrupt': 'Interruption of the loading in the content buffer',
    'connection': 'Connection for delivery of "%s": persistent = %s - partial requests = %s',
    'yes': 'yes',
    'no': 'no',
    'indexation': 'Indexation of the buffer on the connection %d',
    'deindexation': 'Deindexation of the buffer',
    'translation': 'Translation of the buffer to the position %d',
    'present': 'Segment %d -> already present in the zone %d of the buffer'
  },
  'mediaserver': {
    'connection': 'Connection to the delivery server of %s:%s',
    'deliverystart': 'Connection %d -> start of the delivery of the content to %s:%s',
    'delivery1': 'Connection %d -> segment %d -> delivery from the zone %d of the buffer',
    'delivery2': 'Connection %d -> segment %d -> delivery',
    'delivery3': 'Connection %d -> segment %d -> delivery from the buffer',
    'exceeded': 'Connection %d -> segment %d -> the zone %d has been exceeded by the tail of the buffer',
    'expulsion': 'Connection %d -> segment %d -> expulsion of the buffer',
    'failure': 'Connection %d -> segment %d -> failure of the delivery of the content',
    'deliveryfailure': 'Connection %d -> failure of the delivery of the content',
    'deliverystop': 'Connection %d -> end of the delivery of the content',
    'subdelivery': 'Delivery of the subtitles to %s:%s',
    'subfailure': 'Failure of the delivery of the subtitles to %s:%s',
    'start': 'Start, on the interrface %s, of the delivery server in %s mode%s',
    'sequential': 'sequential',
    'random': 'random',
    'unsupported': ' unsupported by the source',
    'shutdown': 'Shutdown of the delivery server'
  },
  'dlnanotification': {
    'start': 'Start of the server of listening of event notifications from DLNA %s at the address %s:%s',
    'stop': 'Shutdown of the server of listening of event notifications from DLNA %s at the address %s:%s',
    'alreadyactivated': 'Server of listening of event notifications from DLNA %s at the address %s:%s already activated',
    'receipt': 'DLNA Renderer %s -> service %s -> receipt of the notification of event %s',
    'notification': 'DLNA Renderer %s -> Service %s -> notification of event %s -> %s is changed to %s',
    'alert': 'DLNA Renderer %s -> Service %s -> notification of event %s -> alerte: %s is changed to %s'
  },
  'dlnaadvertisement': {
    'receipt': 'Receipt, on the interface %s, of an advertisement from the device %s (%s:%s): %s',
    'ignored': 'Advertisement of the device %s (%s:%s) ignored due to the mismatch of the address of the description URL',
    'set': 'Installation of the listening of advertisements of DLNA devices on the interface %s',
    'fail': 'Failure of the installation of the listening of advertisements of DLNA devices on the interface %s',
    'alreadyactivated': 'Listening of advertisements of DLNA devices already activated',
    'start': 'Start of the server of listening of advertisements of DLNA devices',
    'stop': 'Shutdown of the server of listening of advertisements of DLNA devices'
  },
  'dlnahandler': {
    'ip_failure': 'Failure of the retrieval of the host ip address',
    'registering': 'Registration of the %s %s on the interface %s',
    'msearch1': 'Sending of a search message of uuid:%s',
    'msearch2': 'Sending of a search message of DLNA device',
    'msearch3': 'Sending of a search message of DNLA %s',
    'sent': 'Sending of the search message on the interface %s',
    'fail': 'Failure of the sending of the search message on the interface %s',
    'receipt': 'Receipt, on the interface %s, of a response to the search message from %s:%s',
    'ignored': 'Response from %s:%s ignored due to the mismatch of the address of the description URL',
    'alreadyactivated': 'Search of DNLA %s already activated',
    'start': 'Start of the search of DLNA %s',
    'stop': 'End of the search of DLNA %s',
    'commandabandonment': '%s %s -> service %s -> abandonment of the sending of the command %s',
    'commandsending': '%s %s -> service %s -> sending of the command %s',
    'commandfailure': '%s %s -> service %s -> failure of the sending of the command %s',
    'commandsuccess': '%s %s -> service %s -> success of the sending of the command %s',
    'responsefailure': '%s %s -> service %s -> failure of the processing of the response to the command %s',
    'responsesuccess': '%s %s -> service %s -> success of the receipt of the response to the command %s',
    'advertalreadyactivated': 'Listening of the advertisements of %s already activated',
    'advertstart': 'Start of the listening of advertisements of %s',
    'advertstop': 'End of the listening of advertisements of %s',
    'subscralreadyactivated': 'Renderer %s -> service %s -> subscription to the events server already in place',
    'subscrfailure': 'Renderer %s -> service %s -> failure of the request of subscription to the events server',
    'subscrsuccess': 'Renderer %s -> service %s -> subscription to the events server under the SID %s for a period of %s',
    'subscrrenewfailure': 'Renderer %s -> service %s -> failure of the request of renewal of subscription under SID %s to the events server',
    'subscrrenewsuccess': 'Renderer %s -> service %s -> renewal of the subscription under SID %s to the events server for a period of %s',
    'subscrunsubscrfailure': 'Renderer %s -> service %s -> failure of the request of end of subscription under SID %s to the events server',
    'subscrunsubscrsuccess': 'Renderer %s -> service %s -> end of subscription under SID %s to the events server'
  },
  'websocket': {
    'endacksuccess': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> success of the sending of the acknowledgment of receipt of the notice of end of connection',
    'endackfailure': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> failure of the sending of the acknowledgment of receipt of the notice of end of connection',
    'errorendnotification': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> sending of a notice of end of connection because of error %s',
    'errorendnotificationsuccess': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> success of the sending of the notice of end of connection',
    'errorendnotificationfailure': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> failure of the sending of the notice of end of connection',
    'terminationdatasuccess': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> success of the sending of the termination data %s',
    'terminationdatafailure': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> failure of the sending of the termination data %s',
    'endnotificationsuccess': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> success of the sending of the notice of end of connection',
    'endnotificationfailure': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> failure of the sending of the notice of end of connection',
    'datasuccess': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> sending of the data %s',
    'datafailure': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> failure of the sending of the data %s',
    'datareceipt': 'WebSocket server %s:%s/%s -> WebSocket %s:%s -> receipt of the data %s',
    'connectionrequest': 'WebSocket server %s:%s -> connection request from the WebSocket %s:%s',
    'connectionrequestinvalid': 'WebSocket server %s:%s -> connection request from the WebSocket %s:%s invalid',
    'connectionrequestnotfound': 'WebSocket server %s:%s -> path of the connection request from the WebSocket %s:%s not found: /%s',
    'connectionresponsefailure': 'WebSocket server %s:%s/%s -> failure of the sending of the response to the connection request from the WebSocket %s:%s',
    'connection': 'WebSocket server %s:%s/%s -> connection to the WebSocket %s:%s',
    'endack': 'WebSocket server %s:%s/%s -> acknowledgment of end of connection from the WebSocket %s:%s',
    'endnotification': 'WebSocket server %s:%s/%s -> notice of end of connection from the WebSocket %s:%s',
    'connectionend': 'WebSocket server %s:%s/%s -> end of connection to the WebSocket %s:%s',
    'start': 'Start of the server for Websocket at the address %s:%s',
    'fail': 'Failure of the start of the server for Websocket at the address %s:%s',
    'open': 'Websocket server %s:%s: opening of the channel /%s',
    'close': 'Websocket server %s:%s: closure of the channel /%s',
    'shutdown': 'Shutdonw of the server for Websocket at the address %s:%s'
  },
  'webinterface': {
    'ip_failure': 'Failure of the retrieval of the host ip address',
    'connection': 'Connection of the Web interface %s:%s',
    'response': 'Response to the Web interface %s:%s - request: %s',
    'formdatareceipt': 'Receipt of the form data %s from %s:%s',
    'formdatareject': 'Rejection of the form data %s from %s:%s',
    'playbackaccept': 'Acceptance of the playback request of %s%s starting at %s on %s from %s:%s',
    'playbacksub': ' and %s',
    'playbackreject': 'Rejection of the playback request of %s%s starting at %s on %s from %s:%s',
    'rendererstart': 'Start of the display manager of renderer for Web interface server',
    'launchrendererstart': 'Start of the display manager of renderer in the launch form for Web interface server',
    'rendererstop': 'Shutdown of the display manager of renderer for Web interface server',
    'controlstart': 'Start of the playback controller manager for Web interface server',
    'controlinterrupt': 'Interruption of the playback controller manager for Web interface server',
    'controlrenderer': 'Selection of the renderer %s on the interface %s',
    'playlist': 'Playlist generated from the address %s: %s media contents',
    'nocontent': 'Absence of media content under the address %s',
    'nonegapless': 'Absence of support of gapless playback by the renderer %s',
    'gapless': 'Gapless playback of the media contents from the address %s enabled',
    'nogapless': 'Address %s incompatible with gapless playback',
    'norendereranswer': 'Absence of response from the renderer %s',
    'ready': 'Ready for playback of "%s"%s, by %s, on the renderer "%s"',
    'subtitled': ', subtitled',
    'direct': 'direct transmission of the address',
    'random': 'delivery through server in random access mode',
    'sequential': 'delivery through server in sequential access mode%s',
    'remuxed': ', remuxed in %s',
    'controlstop': 'Shutdown of the playback controller manager for Web interface server%s%s%s%s',
    'status': ' - status ',
    'start': 'Start of the Web interface server on the interface %s',
    'alreadyrunning': 'Web interface server already in place',
    'fail': 'Failure of the start of the Web interface server on the interface %s',
    'shutdown': 'Shutdown of the Web interface server',
    'jstart': 'Launch interface',
    'jcontrol': 'Control interface',
    'jrenderers': 'Renderers',
    'jmwebsocketfailure': 'Failure of the establishment of the WebSocket connection',
    'jmrenderersclosed': 'Renderers - interface closed',
    'jmentervalidurl': 'Enter a valid media content URL',
    'jmentervalidsuburl': 'Enter a valid subtitles URL',
    'jmselectrenderer': 'First select a renderer',
    'jplaybackposition': 'Playback position',
    'jgoplay': 'Play',    
    'jreset': 'Reset',
    'jplay': 'Play',
    'jpause': 'Pause',
    'jstop': 'Stop',
    'jinterfaceclosed': 'interface closed',
    'jback': 'back',
    'jinitialization': 'initialization',
    'jready': 'ready',
    'jreadyfromstart': 'ready (playback from the beginning)',
    'jinprogress': 'in progress',
    'jinplayback': 'playback',
    'jinpause': 'pause',
    'jinstop': 'stop',
    'jplaylist': 'Playlist',
    'jurl': 'Media URL',
    'jstatus': 'Status',
    'jtargetposition': 'Target position',
    'jmstop': 'Stop the playback ?'
  },
  'parser': {
    'license': 'This program is licensed under the GNU GPLv3 copyleft license (see https://www.gnu.org/licenses)',
    'help': 'display of the help message and interruption of the script',
    'ip': 'IP address of the web interface [auto-selected by default - "0.0.0.0", meaning all interfaces, if option present with no address mention]',
    'port': 'TCP port of the web interface [8000 by default]',
    'hip': 'IP address of the DLNA controller/client [auto-selected by default - "0.0.0.0", meaning all interfaces, if option present with no address mention]',
    'rendereruuid': 'uuid of the renderer [first renderer without selection on the uuid by default]',
    'renderername': 'name of the renderer [first renderer without selection on the name by default]',
    'servertype': 'type of server (a:auto, s:sequential, r:random, g:gapless/random, n:none) [a by default]',
    'buffersize': 'size of the buffer in blocks of 1 MB [75 by default]',
    'bufferahead': 'size of the sub-buffer of loading in advance in blocks of 1 MB [25 by default]',
    'muxcontainer': 'type of remuxing container preceded by ! so that it is systematic [MP4 by default]',
    'onreadyplay': 'direct playback as soon as the media content and the renderer are ready [disabled by default]',
    'displayrenderers': 'Displays the renderers present on the network',
    'start': 'Starts the interface from the launch page',
    'control': 'Starts the interface from the control page',
    'mediasrc1': 'adress of the multimedia content [none by default]',
    'mediasrc2': 'adress of the multimedia content',
    'mediasubsrc': 'adress of the subtitles content [none by default]',
    'mediasublang': 'language of the subtitles, . for no selection [en,eng,en.* by default]',
    'mediasublangcode': 'en,eng,en.*',
    'mediastartfrom': 'start time position or display duration in format H:MM:SS [start/indefinite by default]',
    'slideshowduration': 'display duration of the pictures, if mediastrartfrom not defined, in the format H:MM:SS [none by default]',
    'endless': 'loop playback [disabled by default, always enabled in list random playback mode]',
    'verbosity': 'verbosity level from 0 to 2 [0 by default]',
    'stopkey': 'Press "S" to stop',
    'auto': 'auto',
    'sequential': 'sequential',
    'random': 'random',
    'remuxkey': 'Press "!" and "M" to switch between the remuxing modes (MP4, MPEGTS, !MP4, !MPEGTS) for the next playback session - current mode: %s',
    'servertypekey': 'Press "T" to switch between the types of server (auto, sequential, random) for the next playback session - current mode: %s',
    'endlesskey': 'Press "E" to enable/disable the loop playback - current mode: %s',
    'enabled': 'enabled',
    'disabled': 'disabled',
    'remuxnext': 'Remuxing mode for the next playback session: %s',
    'servertypenext': 'Type of server for the next playback session: %s',
    'endlessstatus': 'Loop playback: %s'
  }
}
LSTRINGS = EN_STRINGS
try:
  if locale.getlocale()[0][:2].lower() == 'fr':
    LSTRINGS = FR_STRINGS
except:
  pass


class DLNAEventWarning:

  def __init__(self, event_listener, prop_name, *warn_values, WarningEvent=None):
    self.EventListener = event_listener
    self.WatchedProperty = prop_name
    self.WarningEvent = WarningEvent
    self.WatchedValues = warn_values or None
    self.Triggered = None
    self.TriggerSEQ = None
    self.TriggerLastValue = None
    self.lock = threading.RLock()

  def clear(self):
    with self.lock:
      self.TriggerLastValue = None
      self.TriggerSEQ = self.EventListener.CurrentSEQ
      self.Triggered = None

  def submit(self, seq, prop_name, prop_nvalue):
    if prop_name == self.WatchedProperty:
      with self.lock:
        warn_update = True if (self.TriggerSEQ is None) else (self.TriggerSEQ < seq)
        if warn_update and self.WatchedValues:
          warn_update = prop_nvalue in self.WatchedValues
        if warn_update:
          self.TriggerLastValue = prop_nvalue
          self.TriggerSEQ = seq
          self.Triggered = True
          if self.WarningEvent is not None:
            self.WarningEvent.set()
          return True
    return False

  def fresh(self):
    with self.lock:
      if self.Triggered:
        self.Triggered = False
        return self.TriggerLastValue
    return None

  def last(self):
    return self.TriggerLastValue


def _XMLGetNodeText(node):
  text = []
  for childNode in node.childNodes:
    if childNode.nodeType == node.TEXT_NODE:
      text.append(childNode.data)
  return(''.join(text))

def _XMLGetRTagElements(node, tag):
  return node.getElementsByTagNameNS('urn:schemas-upnp-org:device-1-0', tag) or node.getElementsByTagNameNS('*', tag)

def _XMLGetSTagElements(node, tag):
  return node.getElementsByTagNameNS('urn:schemas-upnp-org:service-1-0', tag) or node.getElementsByTagNameNS('*', tag)

def _XMLGetRTagText(node, tag):
  return _XMLGetNodeText(_XMLGetRTagElements(node, tag)[0])

def _XMLGetSTagText(node, tag):
  return _XMLGetNodeText(_XMLGetSTagElements(node, tag)[0])


class DLNADevice:

  DEVICE_TYPE = 'Device'

  def __init__(self):
    self.DescURL = None
    self.BaseURL = None
    self.Ip = None
    self.Manufacturer = None
    self.ModelName = None
    self.FriendlyName = None
    self.ModelDesc = None
    self.ModelNumber = None
    self.SerialNumber = None
    self.UDN = None
    self.IconURL = None
    self.Services = []
    self.StatusAlive = None
    self.StatusTime = None
    self.StatusAliveLastTime = None

class DLNAService:

  def __init__(self):
    self.Type = None
    self.Id = None
    self.ControlURL = None
    self.SubscrEventURL = None
    self.DescURL = None
    self.Actions = []
    self.EventThroughLastChange = None

class DLNAAction:

  def __init__(self):
    self.Name = None
    self.Arguments = []

class DLNAArgument:

  def __init__(self):
    self.Name = None
    self.Direction = None
    self.Event = None
    self.Type = None
    self.AllowedValueList = None
    self.AllowedValueRange = None
    self.DefaultValue = None

class DLNAEventListener:

  def __init__(self, log):
    self.event_notification_listener = None
    self.SID = None
    self.Device = None
    self.Service = None
    self.hip = None
    self.callback_number = None
    self.log = log
    self.EventsLog = []
    self.CurrentSEQ = None
    self.Warnings = []
    self.is_running = None

class DLNAEvent:

  def __init__(self):
    self.ReceiptTime = None
    self.Changes = []

class DLNARenderer(DLNADevice):

  DEVICE_TYPE = 'Renderer'

class DLNAServer(DLNADevice):

  DEVICE_TYPE = 'Server'

class DLNAEventNotificationServer(socketserver.TCPServer):

  request_queue_size = 100

  def __init__(self, *args, verbosity, **kwargs):
    self.logger = log_event('dlnanotification', verbosity)
    super().__init__(*args, **kwargs)
    self.__dict__['_BaseServer__is_shut_down'].set()
  
  def server_bind(self):
    try:
      self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    except:
      pass
    super().server_bind()

  def shutdown(self):
    self.socket.close()
    super().shutdown()

  def server_close(self):
    pass

class DLNAEventNotificationHandler(socketserver.BaseRequestHandler):

  def __init__(self, *args, EventListeners, process_lastchange, **kwargs):
    self.EventListeners = EventListeners
    self.process_lastchange = process_lastchange
    try:
      super().__init__(*args, **kwargs)
    except:
      pass
  
  def handle(self):
    try:
      req = HTTPMessage(self.request)
      event_listeners = list(self.EventListeners)
      if req.method != 'NOTIFY':
        raise
      callback_number = int(req.path.strip(' /'))
      EventListener = next(e for e in event_listeners if e.callback_number == callback_number)
      if req.header('SID', '') != EventListener.SID:
        raise
      dlna_event = DLNAEvent()
      seq = req.header('SEQ', '')
      self.server.logger.log(1, 'receipt', EventListener.Device.FriendlyName, EventListener.Service.Id[23:], seq)
      seq = int(seq)
      if EventListener.CurrentSEQ is None:
        EventListener.CurrentSEQ = seq
      elif seq > EventListener.CurrentSEQ:
        EventListener.CurrentSEQ = seq
      if EventListener.log:
        dlna_event.ReceiptTime = time.localtime()
        if len(EventListener.EventsLog) < seq:
          EventListener.EventsLog = EventListener.EventsLog + [None]*(seq - len(EventListener.EventsLog))
      root_xml = minidom.parseString(req.body)
      try:
        self.request.sendall("HTTP/1.0 200 OK\r\nContent-Length: 0\r\n\r\n".encode("ISO-8859-1"))
      except:
        pass
    except:
      self.request.sendall("HTTP/1.0 400 Bad Request\r\nContent-Length: 0\r\n\r\n".encode("ISO-8859-1"))
      return
    try:
      for node in root_xml.documentElement.childNodes:
        if node.nodeType != node.ELEMENT_NODE:
          continue
        if node.localName.lower() != 'property':
          continue
        for child_node in node.childNodes:
          try:
            prop_name = child_node.localName
          except:
            continue
          try:
            prop_nvalue = _XMLGetNodeText(child_node)
          except:
            continue
          self.server.logger.log(2, 'notification', EventListener.Device.FriendlyName, EventListener.Service.Id[23:], seq, prop_name, prop_nvalue)
          if prop_name.upper() == 'LastChange'.upper():
            try:
              dlna_event.Changes.extend(self.process_lastchange(prop_nvalue))
            except:
              dlna_event.Changes.append((prop_name, prop_nvalue))
          else:
            dlna_event.Changes.append((prop_name, prop_nvalue))
      if EventListener.log:
        EventListener.EventsLog.append(dlna_event)
      for (prop_name, prop_nvalue) in dlna_event.Changes:
        for warning in EventListener.Warnings:
          if warning.submit(seq, prop_name, prop_nvalue):
            self.server.logger.log(2, 'alert', EventListener.Device.FriendlyName, EventListener.Service.Id[23:], seq, prop_name, prop_nvalue)
    except:
      return

class DLNAEventNotificationListener:

  def __init__(self, handler, port, private=False):
    self.logger = log_event('dlnanotification', handler.verbosity)
    self.Handler = handler
    self.port = port
    self.private = private
    self.EventListeners = []
    self.seq = 0
    self.receiver_thread = None
    self.is_running = None

  def register(self, eventlistener):
    if not self.private or not self.seq:
      self.EventListeners.append(eventlistener)
      self.seq += 1
      return self.seq
    else:
      return None

  def unregister(self, eventlistener):
    try:
      self.EventListeners.remove(eventlistener)
      return True
    except:
      return False

  def _start_event_notification_receiver(self, server_ready):
    DLNAEventNotificationBoundHandler = partial(DLNAEventNotificationHandler, process_lastchange=self.Handler._process_lastchange, EventListeners=self.EventListeners)
    try:
      with DLNAEventNotificationServer((self.Handler.ip, self.port), DLNAEventNotificationBoundHandler, verbosity=self.Handler.verbosity) as self.DLNAEventNotificationReceiver:
        server_ready.set()
        self.DLNAEventNotificationReceiver.serve_forever()
    except:
      server_ready.set()
    self.is_running = None

  def _shutdown_event_notification_receiver(self):
    if self.is_running:
      self.is_running = False
      try:
        self.DLNAEventNotificationReceiver.shutdown()
        self.receiver_thread.join()
      except:
        pass

  def start(self):
    if self.is_running:
      self.logger.log(1, 'alreadyactivated', self.Handler.DEVICE_TYPE, self.Handler.ip, self.port)
      return None
    self.is_running = True
    self.logger.log(1, 'start', self.Handler.DEVICE_TYPE, self.Handler.ip, self.port)
    server_ready = threading.Event()
    self.receiver_thread = threading.Thread(target=self._start_event_notification_receiver, args=(server_ready,))
    self.receiver_thread.start()
    server_ready.wait()

  def stop(self):
    if self.is_running:
      self._shutdown_event_notification_receiver()
      self.logger.log(1, 'stop', self.Handler.DEVICE_TYPE, self.Handler.ip, self.port)

class DLNAAdvertisementServer:

  def __init__(self, handlers, verbosity):
    self.logger = log_event('dlnaadvertisement', verbosity)
    self.Handlers = handlers
    self.__shutdown_request = False
    self.__is_shut_down = threading.Event()
    self.__is_shut_down.set()
    self.Sockets = ()
    self.Ips = ()

  def _handle(self, i, msg, addr):
    sock = self.Sockets[i]
    ip = self.Ips[i]
    try:
      req = HTTPMessage((msg, sock))
      if req.method != 'NOTIFY':
        return
      nt = req.header('NT', '')
      only_media = True
      for handler in self.Handlers:
        if not handler.DEVICE_TYPE.lower() in ('renderer', 'server'):
          only_media = False
          break
      if only_media and not 'media' in nt.lower():
        return
      time_req = time.localtime()
      nts = req.header('NTS', '')
      usn = req.header('USN', '')
      udn = usn[0:6] + usn[6:].split(':', 1)[0]
      desc_url = req.header('Location','')
      self.logger.log(2, 'receipt', ip, usn, *addr, nts)
      dip = urllib.parse.urlparse(desc_url).netloc.split(':', 1)[0]
      for handler in self.Handlers:
        if not ip in handler.ips:
          continue
        if handler.DEVICE_TYPE.lower() != 'device':
          if not ('Media' + handler.DEVICE_TYPE).lower() in nt.lower():
            continue
        if 'alive' in nts.lower():
          for dev in handler.Devices:
            if dev.DescURL == desc_url and dev.UDN == udn:
              if dev.StatusAlive:
                if dev.StatusTime < time_req:
                  dev.StatusTime = time_req
                  dev.StatusAliveLastTime = time_req
              else:
                handler._update_devices(desc_url, time_req, ip, handler.advert_status_change)
              break
          else:
            if dip == addr[0]:
              handler._update_devices(desc_url, time_req, ip, handler.advert_status_change)
            else:
              self.logger.log(2, 'ignored', usn, *addr)
        elif 'byebye' in nts.lower():
          for dev in handler.Devices:
            if dev.DescURL == desc_url and dev.UDN == udn:
              if dev.StatusAlive:
                dev.StatusAlive = False
                handler.advert_status_change.set()
              dev.StatusTime = time_req
              break
    except:
      return

  def handle(self, i, msg, addr):
    t = threading.Thread(target=self._handle, args=(i, msg, addr), daemon=True)
    t.start()

  def serve_forever(self):
    self.__is_shut_down.clear()
    self.__shutdown_request = False
    can_run = False
    self.Ips = tuple(set(ip for handler in self.Handlers for ip in handler.ips))
    self.Sockets = tuple(socket.socket(type=socket.SOCK_DGRAM) for ip in self.Ips)
    with selectors.DefaultSelector() as selector:
      for i in range(len(self.Ips)):
        sock = self.Sockets[i]
        ip = self.Ips[i]
        try:
          sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          sock.bind((ip, 1900))
          sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, struct.pack('4s4s', socket.inet_aton('239.255.255.250'), socket.inet_aton(ip)))
          selector.register(sock, selectors.EVENT_READ, i)
          self.logger.log(2, 'set', ip)
          can_run = True
        except:
          self.logger.log(1, 'fail', ip)
      if not can_run:
        self.__shutdown_request = True
      while not self.__shutdown_request:
        try:
          ready = selector.select(0.5)
          if self.__shutdown_request:
            break
          for r in ready:
            try:
              self.handle(r[0].data, *self.Sockets[r[0].data].recvfrom(8192))
            except:
              pass
        except:
          pass
    self.__shutdown_request = False
    self.__is_shut_down.set()

  def shutdown(self):
    self.__shutdown_request = True
    for sock in self.Sockets:
      try:
        sock.close()
      except:
        pass
    self.__is_shut_down.wait()

  def __enter__(self):
    return self

  def __exit__(self, *args):
    pass

class DLNAAdvertisementListener:

  def __init__(self, handlers=[], verbosity=0):
    self.DLNAHandlers = handlers
    for handler in handlers:
      handler.advertisement_listener = self
    self.is_advert_receiver_running = None
    self.verbosity = verbosity
    self.logger = log_event('dlnaadvertisement', verbosity)

  def _start_advertisement_receiver(self):
    with DLNAAdvertisementServer(self.DLNAHandlers, self.verbosity) as self.DLNAAdvertisementReceiver:
      self.DLNAAdvertisementReceiver.serve_forever()
    self.is_advert_receiver_running = None
    for handler in self.DLNAHandlers:
      handler.is_advert_receiver_running = None

  def _shutdown_advertisement_receiver(self):
    if self.is_advert_receiver_running:
      try:
        self.DLNAAdvertisementReceiver.shutdown()
      except:
        pass
    self.is_advert_receiver_running = False
    for handler in self.DLNAHandlers:
      handler.is_advert_receiver_running = False

  def start(self):
    if self.is_advert_receiver_running:
      self.logger.log(1, 'alreadyactivated')
      return False
    else:
      self.is_advert_receiver_running = True
      for handler in self.DLNAHandlers:
        handler.is_advert_receiver_running = True
      self.logger.log(1, 'start')
      for handler in self.DLNAHandlers:
        if not isinstance(handler.advert_status_change, threading.Event):
          handler.advert_status_change = threading.Event()
      receiver_thread = threading.Thread(target=self._start_advertisement_receiver)
      receiver_thread.start()
      return True
  
  def stop(self):
    if self.is_advert_receiver_running:
      self.logger.log(1, 'stop')
      self._shutdown_advertisement_receiver()

  def wait(self, handler, timeout=None):
    adv_event = None
    try:
      adv_event = handler.advert_status_change.wait(timeout)
    except:
      pass
    if adv_event:
      handler.advert_status_change.clear()
    return adv_event


class DLNAHandler:

  DEVICE_TYPE = 'Device'

  @staticmethod
  def retrieve_ips():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
      st.connect(('10.255.255.255', 1))
      IP = st.getsockname()[0]
    except Exception:
      IP  = '127.0.0.1'
    finally:
      st.close()
    IP = str(IP)
    IP = (IP,)
    return IP

  def __init__(self, ip='', verbosity=0):
    self.Devices = []
    self.Hips = []
    self.verbosity = verbosity
    self.logger = log_event('dlnahandler', verbosity)
    self.advertisement_listener = None
    self.is_advert_receiver_running = None
    self.advert_status_change = None
    self.is_discovery_polling_running = None
    self.discovery_status_change = None
    self.discovery_polling_shutdown = None
    if ip:
      self.ip = ip
    else:
      try:
        s = socket.socket(type=socket.SOCK_DGRAM)
        s.connect(('239.255.255.250', 1900))
        self.ip = s.getsockname()[0]
        s.close()
      except:
        try:
          self.ip = socket.gethostbyname(socket.gethostname())
        except:
          try:
            self.ip = socket.gethostbyname(socket.getfqdn())
          except:
            self.ip = '0.0.0.0'
            self.logger.log(LSTRINGS['ip_failure'], 0)
    if socket.inet_aton(self.ip) != b'\x00\x00\x00\x00':
      self.ips = (self.ip,)
    else:
      self.ips = self.retrieve_ips()
    self.update_devices = threading.Lock()

  def _update_devices(self, desc_url, time_msg, hip, status_change=None, cond_numb=None):
    try:
      resp = HTTPRequest(desc_url, timeout=5, ip=hip)
      if resp.code != '200':
        raise
      root_xml = minidom.parseString(resp.body)
      if not ('Media' + self.DEVICE_TYPE).lower() in _XMLGetRTagText(root_xml, 'deviceType').lower():
        raise
      udn = _XMLGetRTagText(root_xml, 'UDN')
      self.update_devices.acquire()
      dind = None
      try:
        for d, dev in enumerate(self.Devices):
          if dev.DescURL == desc_url and dev.UDN == udn:
            if dev.StatusAlive:
              if dev.StatusTime < time_msg:
                dev.StatusTime = time_msg
                dev.StatusAliveLastTime = time_msg
              raise
            dind = d
            break
        try:
          device = eval('DLNA' + self.DEVICE_TYPE + '()')
        except:
          device = DLNADevice()
        device.Ip = urllib.parse.urlparse(desc_url).netloc.split(':', 1)[0]
        baseurl_elem = _XMLGetRTagElements(root_xml, 'URLBase')
        if baseurl_elem:
          baseurl = _XMLGetNodeText(baseurl_elem[0])
          if urllib.parse.urlparse(baseurl).netloc.split(':', 1)[0] != device.Ip:
            raise
        else:
          baseurl = desc_url
      except:
        self.update_devices.release()
        raise
    except:
      if cond_numb:
        with cond_numb[0]:
          cond_numb[1] += 1
          cond_numb[0].notify()
      return False
    try:
      device.IconURL = None
      nodes_ic = _XMLGetRTagElements(root_xml, 'icon')
      for node_ic in reversed(nodes_ic):
        try:
          if 'png' in _XMLGetRTagText(node_ic, 'mimetype').lower():
            device.IconURL = urllib.parse.urljoin(baseurl, _XMLGetRTagText(node_ic, 'url'))
        except:
          pass
      if not device.IconURL:
        try:
          device.IconURL = urllib.parse.urljoin(baseurl, _XMLGetRTagText(_XMLGetRTagElements(root_xml, 'icon')[-1], 'url'))
        except:
          device.IconURL = ''
      if device.IconURL:
        if urllib.parse.urlparse(device.IconURL).netloc.split(':', 1)[0] != device.Ip:
          iconurl = ''
    except:
      pass
    try:
      device.FriendlyName = _XMLGetRTagText(root_xml, 'friendlyName')
    except:
      device.FriendlyName = ''
    device.DescURL = desc_url
    device.UDN = udn
    device.StatusAlive = True
    device.StatusTime = time_msg
    device.StatusAliveLastTime = time_msg
    if dind is None:
      self.Hips.append(hip)
      self.Devices.append(device)
    else:
      self.Hips[d] = hip
      self.Devices[d] = device
    self.update_devices.release()
    if cond_numb:
      with cond_numb[0]:
        cond_numb[1] += 1
        cond_numb[0].notify()
    try:
      device.Manufacturer = _XMLGetRTagText(root_xml, 'manufacturer')
    except:
      pass
    try:
      device.ModelName = _XMLGetRTagText(root_xml, 'modelName')
    except:
      pass
    if dind is None:
      self.logger.log(1, 'registering', self.DEVICE_TYPE.lower(), device.FriendlyName, hip)
    try:
      device.ModelDesc = _XMLGetRTagText(root_xml, 'modelDescription')
    except:
      pass
    try:
      device.ModelNumber = _XMLGetRTagText(root_xml, 'modelNumber')
    except:
      pass
    try:
      device.SerialNumber = _XMLGetRTagText(root_xml, 'serialNumber')
    except:
      pass
    for node in _XMLGetRTagElements(root_xml, 'service'):
      service = DLNAService()
      try:
        service.Type = _XMLGetRTagText(node, 'serviceType')
        service.Id = _XMLGetRTagText(node, 'serviceId')
        service.ControlURL = urllib.parse.urljoin(baseurl, _XMLGetRTagText(node, 'controlURL'))
        if urllib.parse.urlparse(service.ControlURL).netloc.split(':', 1)[0] != device.Ip:
          continue
        service.SubscrEventURL = urllib.parse.urljoin(baseurl, _XMLGetRTagText(node, 'eventSubURL'))
        if urllib.parse.urlparse(service.SubscrEventURL).netloc.split(':', 1)[0] != device.Ip:
          continue
        service.DescURL = urllib.parse.urljoin(baseurl, _XMLGetRTagText(node, 'SCPDURL'))
        if urllib.parse.urlparse(service.DescURL).netloc.split(':', 1)[0] != device.Ip:
          continue
      except:
        continue
      try:
        resp = HTTPRequest(service.DescURL, timeout=5, ip=hip)
        if resp.code != '200':
          raise
      except:
        continue
      root_s_xml = minidom.parseString(resp.body)
      for node_s in _XMLGetSTagElements(root_s_xml, 'action'):
        action = DLNAAction()
        try:
          action.Name = _XMLGetSTagText(node_s, 'name')
        except:
          continue
        for node_a in _XMLGetSTagElements(node_s, 'argument'):
          argument = DLNAArgument()
          try:
            argument.Name = _XMLGetSTagText(node_a, 'name')
            argument.Direction = _XMLGetSTagText(node_a, 'direction')
            statevar = _XMLGetSTagText(node_a, 'relatedStateVariable')
            node_sv = next(sv for sv in _XMLGetSTagElements(root_s_xml, 'stateVariable') if _XMLGetSTagElements(sv, 'name')[0].childNodes[0].data == statevar)
            if node_sv.getAttribute('sendEvents') == 'yes':
              argument.Event = True
            elif node_sv.getAttribute('sendEvents') == 'no':
              argument.Event = False
            argument.Type = _XMLGetSTagText(node_sv, 'dataType')
            try:
              node_sv_av = _XMLGetSTagElements(node_sv, 'allowedValueList')[0]
              argument.AllowedValueList = *(_XMLGetNodeText(av) for av in _XMLGetSTagElements(node_sv_av,'allowedValue')),
            except:
              pass
            try:
              node_sv_ar = _XMLGetSTagElements(node_sv, 'allowedValueRange')[0]
              argument.AllowedValueRange = (_XMLGetSTagText(node_sv_ar, 'minimum'), _XMLGetSTagText(node_sv_ar, 'maximum'))
            except:
              pass
            try:
              argument.DefaultValue = _XMLGetSTagText(node_sv, 'defaultValue')
            except:
              pass
          except:
            argument = None
            continue
          if argument:
            action.Arguments.append(argument)
          else:
            action = None
            break
        if action:
          service.Actions.append(action)
      service.EventThroughLastChange = False
      try:
        node_sv = next(sv for sv in _XMLGetSTagElements(root_s_xml, 'stateVariable') if _XMLGetSTagElements(sv, 'name')[0].childNodes[0].data.upper() == 'LastChange'.upper())
        if node_sv.getAttribute('sendEvents') == 'yes':
          service.EventThroughLastChange = True
      except:
        pass
      device.Services.append(service)
    device.BaseURL = baseurl
    if status_change:
      try:
        status_change.set()
      except:
        pass
    return True

  def _discover(self, uuid=None, timeout=2, alive_persistence=0, from_polling=False):
    if uuid:
      self.logger.log(2, 'msearch1', uuid)
      msg = \
      'M-SEARCH * HTTP/1.1\r\n' \
      'HOST: 239.255.255.250:1900\r\n' \
      'ST: uuid:' + uuid + '\r\n' \
      'MX: 2\r\n' \
      'MAN: "ssdp:discover"\r\n' \
      '\r\n'
    elif self.DEVICE_TYPE == 'Device':
      self.logger.log(2, 'msearch2')
      msg = \
      'M-SEARCH * HTTP/1.1\r\n' \
      'HOST: 239.255.255.250:1900\r\n' \
      'ST: upnp:rootdevice\r\n' \
      'MX: 2\r\n' \
      'MAN: "ssdp:discover"\r\n' \
      '\r\n'
    else:
      self.logger.log(2, 'msearch3', self.DEVICE_TYPE.lower())
      msg = \
      'M-SEARCH * HTTP/1.1\r\n' \
      'HOST: 239.255.255.250:1900\r\n' \
      'ST: urn:schemas-upnp-org:device:Media%s:1\r\n' \
      'MX: 2\r\n' \
      'MAN: "ssdp:discover"\r\n' \
      '\r\n' % self.DEVICE_TYPE
    socks = []
    for ip in self.ips:
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
      sock.settimeout(timeout)
      socks.append(sock)
      try:
        sock.bind((ip, 0))
        try:
          sock.sendto(msg.encode("ISO-8859-1"), (ip, 1900))
        except:
          pass
        try:
          sock.sendto(msg.encode("ISO-8859-1"), ('239.255.255.250', 1900))
          self.logger.log(2, 'sent', ip)
        except:
          self.logger.log(1, 'fail', ip)
      except:
        self.logger.log(1, 'fail', ip)
    loca_time_hip = []
    stopped = False
    time_req = time.localtime()
    with selectors.DefaultSelector() as selector:
      for i in range(len(self.ips)):
        try:
          selector.register(socks[i], selectors.EVENT_READ, i)
        except:
          pass
      start_time = time.monotonic()
      tupds = []
      if from_polling:
        cond_numb = [threading.Condition(), 0]
      else:
        cond_numb = None
      while time.monotonic() - start_time <= timeout and (not from_polling or self.is_discovery_polling_running):
        ready = selector.select(0.5)
        for r in ready:
          try:
            sock = socks[r[0].data]
            ip = self.ips[r[0].data]
            resp, addr = sock.recvfrom(65507)
            self.logger.log(2, 'receipt', ip, *addr)
            time_resp = time.localtime()
            try:
              resp = HTTPMessage((resp, addr), body=False)
              if resp.code != '200' or not (uuid or ('' if self.DEVICE_TYPE == 'Device' else ('Media' + self.DEVICE_TYPE))).lower() in resp.header('ST', '').lower():
                continue
              loca = resp.header('Location')
              if (urllib.parse.urlparse(loca)).netloc.split(':',1)[0] == addr[0]:
                t = threading.Thread(target=self._update_devices, args=(loca, time_resp, ip, self.discovery_status_change if from_polling else None, cond_numb), daemon=True)
                tupds.append(t)
                t.start()
              else:
                self.logger.log(2, 'ignored', *addr)
            except:
              pass
          except:
            pass
    time_resp = time.localtime()
    for sock in socks:
      try:
        sock.close()
      except:
        pass
    tot_numb = len(tupds)
    if cond_numb and tot_numb:
      with cond_numb[0]:
        while cond_numb[1] < tot_numb:
          cond_numb[0].wait()
    trimmed = False
    for dev in self.Devices:
      if dev.StatusAlive:
        if (True if not uuid else dev.UDN == 'uuid:' + uuid):
          with self.update_devices:
            if time.mktime(time_req) - time.mktime(dev.StatusAliveLastTime) > alive_persistence:
              dev.StatusAlive = False
              dev.StatusTime = time_resp
              trimmed = True
    if trimmed and from_polling:
      try:
        self.discovery_status_change.set()
      except:
        pass
    if not from_polling:
      for t in tupds:
        t.join()

  def discover(self, uuid=None, timeout=2, alive_persistence=0, from_polling=False):
    if from_polling:
      t = threading.Thread(target=self._discover, args=(uuid, timeout, alive_persistence, from_polling), daemon=True)
      t.start()
      return t
    else:
      self._discover(uuid, timeout, alive_persistence, from_polling)

  def search(self, uuid=None, name=None, complete=False):
    device = None
    for dev in self.Devices:
      if uuid:
        if name:
          if dev.UDN == 'uuid:' + uuid and dev.FriendlyName.lower() == name.lower():
            device = dev
            if dev.StatusAlive and (not complete or dev.BaseURL):
              break
        else:
          if dev.UDN == 'uuid:' + uuid:
            device = dev
            if dev.StatusAlive and (not complete or dev.BaseURL):
              break
      else:
        if name:
          if dev.FriendlyName.lower() == name.lower():
            device = dev
            if dev.StatusAlive and (not complete or dev.BaseURL):
              break
        else:
          if dev.StatusAlive and (not complete or dev.BaseURL):
            device = dev
            break
    return device

  def _discovery_polling(self, timeout=2, alive_persistence=0, polling_period=30):
    self.is_discovery_polling_running = True
    if self.discovery_status_change == None:
      self.discovery_status_change = threading.Event()
    first_time = True
    while self.is_discovery_polling_running and not self.discovery_polling_shutdown.is_set():
      if first_time:
        self.discover(uuid=None, timeout=timeout, alive_persistence=86400, from_polling=True)
      else:
        self.discover(uuid=None, timeout=timeout, alive_persistence=alive_persistence, from_polling=True)
      if not self.is_discovery_polling_running:
        break
      if first_time:
        first_time = False
      self.discovery_polling_shutdown.wait(polling_period)
    self.discovery_polling_shutdown = None
    self.is_discovery_polling_running = None

  def start_discovery_polling(self, timeout=2, alive_persistence=0, polling_period=30, DiscoveryEvent=None):
    if self.is_discovery_polling_running:
      self.logger.log(1, 'alreadyactivated', self.DEVICE_TYPE.lower())
    else:
      self.logger.log(1, 'start', self.DEVICE_TYPE.lower())
      if isinstance(DiscoveryEvent, threading.Event):
        self.discovery_status_change = DiscoveryEvent
      else:
        self.discovery_status_change = threading.Event()
      self.discovery_polling_shutdown = threading.Event()
      discovery_thread = threading.Thread(target=self._discovery_polling, args=(timeout, alive_persistence, polling_period))
      discovery_thread.start()
      return self.discovery_status_change

  def stop_discovery_polling(self):
    try:
      self.discovery_polling_shutdown.set()
    except:
      pass
    if self.is_discovery_polling_running:
      self.logger.log(1, 'stop', self.DEVICE_TYPE.lower())
      self.is_discovery_polling_running = False
      self.discovery_status_change.set()

  def wait_for_discovery(self, timeout=None):
    disc_event = None
    try:
      disc_event = self.discovery_status_change.wait(timeout)
    except:
      pass
    if disc_event:
      self.discovery_status_change.clear()
    if self.is_discovery_polling_running:
      return disc_event
    else:
      return None

  def _build_soap_msg(self, device, service, action, **arguments):
    if not device:
      return None
    serv = next((serv for serv in device.Services if serv.Id == ('urn:upnp-org:serviceId:' + service)), None)
    if not serv:
      return None
    act = next((act for act in serv.Actions if act.Name == action), None)
    if not act :
      return None
    msg_body = \
      '<?xml version="1.0"?>\n' \
      '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\n' \
      '<s:Body>\n' \
      '<u:##action## xmlns:u="urn:schemas-upnp-org:service:##service##:1">\n' \
      '##arguments##' \
      '</u:##action##>\n' \
      '</s:Body>\n' \
      '</s:Envelope>'
    msg_body = msg_body.replace('##service##', service)
    msg_body = msg_body.replace('##action##', action)
    msg_arguments = ''
    cnt_arg = 0
    out_args = {}
    for arg in act.Arguments:
      if arg.Direction == 'in':
        if not arguments:
          return None
        cnt_arg += 1
        if not arg.Name in arguments:
          if arg.DefaultValue:
            arguments[arg.Name] = arg.DefaultValue
          else:
            return None
        msg_arguments = msg_arguments + '<%s>%s</%s>' % (arg.Name, html.escape(str(arguments[arg.Name])) , arg.Name) + '\n'
      if arg.Direction == 'out':
        out_args[arg.Name] = None
    if arguments:
      if len(arguments) > cnt_arg:
        return None
    msg_body = msg_body.replace('##arguments##', msg_arguments)
    msg_body_b = msg_body.encode("utf-8")
    soap_action = 'urn:schemas-upnp-org:service:%s:1#%s' % (service, action)
    msg_headers = {
      'User-Agent': 'PlayOn DLNA Controller',
      'Content-Type': 'text/xml; charset="utf-8"',
      'SOAPAction': '"%s"' % soap_action
    }
    return serv.ControlURL, msg_headers, msg_body_b, out_args

  def send_soap_msg(self, device, service, action, soap_timeout=5, soap_stop=None, **arguments):
    if not device:
      return None
    try:
      ip = self.Hips[self.Devices.index(device)]
    except:
      return None
    cturl_headers_body_oargs = self._build_soap_msg(device, service, action, **arguments)
    if not cturl_headers_body_oargs:
      self.logger.log(1, 'commandabandonment', self.DEVICE_TYPE, device.FriendlyName, service, action)
      return None
    self.logger.log(2, 'commandsending', self.DEVICE_TYPE, device.FriendlyName, service, action)
    resp = HTTPRequest(cturl_headers_body_oargs[0], method='POST', headers=cturl_headers_body_oargs[1], data=cturl_headers_body_oargs[2], timeout=3, max_length=104857600, max_time=soap_timeout+1, stop=soap_stop, ip=ip)
    if resp.code != '200':
      self.logger.log(1, 'commandfailure', self.DEVICE_TYPE, device.FriendlyName, service, action)
      return None
    self.logger.log(1, 'commandsuccess', self.DEVICE_TYPE, device.FriendlyName, service, action)
    try:
      root_xml = minidom.parseString(resp.body)
    except:
      self.logger.log(2, 'responsefailure', self.DEVICE_TYPE, device.FriendlyName, service, action)
      return None
    out_args = cturl_headers_body_oargs[3]
    try:
      for arg in out_args:
        out_args[arg] = _XMLGetNodeText(root_xml.getElementsByTagName(arg)[0])
    except:
      self.logger.log(2, 'responsefailure', self.DEVICE_TYPE, device.FriendlyName, service, action)
      return None
    self.logger.log(2, 'responsesuccess', self.DEVICE_TYPE, device.FriendlyName, service, action)
    if out_args:
      return out_args
    else:
      return True

  def start_advertisement_listening(self, AdvertisementEvent=None):
    if self.is_advert_receiver_running:
      self.logger.log(1, 'advertalreadyactivated', self.DEVICE_TYPE.lower())
    else:
      self.is_advert_receiver_running = True
      self.logger.log(1, 'advertstart', self.DEVICE_TYPE.lower())
      if isinstance(AdvertisementEvent, threading.Event):
        self.advert_status_change = AdvertisementEvent
      else:
        self.advert_status_change = threading.Event()
      self.advertisement_listener = DLNAAdvertisementListener([self], self.verbosity)
      self.advertisement_listener.start()
      return self.advert_status_change
  
  def stop_advertisement_listening(self):
    if self.is_advert_receiver_running:
      self.logger.log(1, 'advertstop', self.DEVICE_TYPE.lower())
      self.advertisement_listener.stop()

  def wait_for_advertisement(self, timeout=None):
    return self.advertisement_listener.wait(self, timeout)

  @staticmethod
  def _process_lastchange(value):
    return [('LastChange', value)]

  def new_event_subscription(self, device, service, port_or_listener, log=False):
    if not device:
      return None
    try:
      hip = self.Hips[self.Devices.index(device)]
    except:
      return None
    serv = next((serv for serv in device.Services if serv.Id == ('urn:upnp-org:serviceId:' + service)), None)
    if not serv:
      return None
    EventListener = DLNAEventListener(log)
    if isinstance(port_or_listener, DLNAEventNotificationListener):
      EventListener.event_notification_listener = port_or_listener
    else:
      try:
        port = int(port_or_listener)
      except:
        return None
      EventListener.event_notification_listener = DLNAEventNotificationListener(self, port, private=True)
    EventListener.callback_number = EventListener.event_notification_listener.register(EventListener)
    if EventListener.callback_number is None:
      return None
    EventListener.Device = device
    EventListener.Service = serv
    EventListener.hip = hip
    return EventListener

  def send_event_subscription(self, EventListener, timeout):
    if not EventListener:
      return None
    msg_headers = {
    'Callback': '<http://%s:%s/%s>' % (EventListener.hip, EventListener.event_notification_listener.port, EventListener.callback_number),
    'NT': 'upnp:event',
    'Timeout': 'Second-%s' % timeout
    }
    if EventListener.is_running:
      self.logger.log(1, 'subscralreadyactivated', EventListener.Device.FriendlyName, EventListener.Service.Id[23:])
      return None
    EventListener.is_running = True
    if EventListener.event_notification_listener.private:
      EventListener.event_notification_listener.start()
    resp = HTTPRequest(EventListener.Service.SubscrEventURL, method='SUBSCRIBE', headers=msg_headers, ip=EventListener.hip, timeout=5)
    if resp.code != '200':
      EventListener.is_running = None
    else:
      EventListener.SID = resp.header('SID', '')
      if not EventListener.SID:
        EventListener.is_running = None
    if EventListener.is_running:
      self.logger.log(1, 'subscrsuccess', EventListener.Device.FriendlyName, EventListener.Service.Id[23:], EventListener.SID, resp.header('TIMEOUT', ''))
      return True
    else:
      EventListener.event_notification_listener.unregister(EventListener)
      self.logger.log(1, 'subscrfailure', EventListener.Device.FriendlyName, EventListener.Service.Id[23:])
      return None
    
  def renew_event_subscription(self, EventListener, timeout):
    if not EventListener:
      return None
    msg_headers = {
    'SID': '%s' % EventListener.SID,
    'Timeout': 'Second-%s' % timeout
    }
    resp = HTTPRequest(EventListener.Service.SubscrEventURL, method='SUBSCRIBE', headers=msg_headers, ip=EventListener.hip, timeout=5)
    if resp.code != '200':
      self.logger.log(1, 'subscrrenewfailure', EventListener.Device.FriendlyName, EventListener.Service.Id[23:], EventListener.SID)
      return None
    self.logger.log(1, 'subscrrenewsuccess', EventListener.Device.FriendlyName, EventListener.Service.Id[23:], EventListener.SID, resp.header('TIMEOUT', ''))
    return True
    
  def send_event_unsubscription(self, EventListener):
    if not EventListener:
      return None
    msg_headers = {
    'SID': '%s' % EventListener.SID
    }
    EventListener.event_notification_listener.unregister(EventListener)
    resp = HTTPRequest(EventListener.Service.SubscrEventURL, method='UNSUBSCRIBE', headers=msg_headers, ip=EventListener.hip, timeout=5)
    if EventListener.event_notification_listener.private:
      EventListener.event_notification_listener.stop()
    if resp.code != '200':
      self.logger.log(1, 'subscrunsubscrfailure', EventListener.Device.FriendlyName, EventListener.Service.Id[23:], EventListener.SID)
      return None 
    self.logger.log(1, 'subscrunsubscrsuccess', EventListener.Device.FriendlyName, EventListener.Service.Id[23:], EventListener.SID)
    return True

  def add_event_warning(self, EventListener, property, *values, WarningEvent=None):
    warning = DLNAEventWarning(EventListener, property, *values, WarningEvent=WarningEvent)
    EventListener.Warnings.append(warning)
    return warning
    
  def wait_for_warning(self, warning, timeout=None, clear=None):
    if clear:
      with warning.lock:
        warning.clear()
        if warning.WarningEvent is not None:
          warning.WarningEvent.clear()
    with warning.lock:
      v = warning.fresh()
      if v is not None:
        if warning.WarningEvent is not None:
          warning.WarningEvent.clear()
        return v
    if warning.WarningEvent is not None:
      if warning.WarningEvent.wait(timeout):
        warning.WarningEvent.clear()
    with warning.lock:
      v = warning.fresh()
      if v is not None:
        if warning.WarningEvent is not None:
          warning.WarningEvent.clear()
        return v
    return None


class DLNAController(DLNAHandler):

  DEVICE_TYPE = 'Renderer'

  def __init__(self, ip='', verbosity=0):
    super().__init__(ip, verbosity)
    self.Renderers = self.Devices

  def _build_didl(self, uri, title, kind=None, size=None, duration=None, suburi=None):
    if size:
      size_arg = ' size="%s"' % (size)
    else:
      size_arg = ''
    if duration:
      duration_arg = ' duration="%s"' % (duration)
    else:
      duration_arg = ''
    media_class = 'object.item.videoItem'
    try:
      if kind.lower() == 'audio':
        media_class = 'object.item.audioItem'
      if kind.lower() == 'image':
        media_class = 'object.item.imageItem'
    except:
      pass
    subtype = None
    try:
      subtype = suburi.rsplit('.', 1)[1]
    except:
      pass
    if not subtype:
      suburi = None
    else:
      if len(subtype) > 4:
        suburi = None
    didl_lite = \
      '<DIDL-Lite '\
      'xmlns:dc="http://purl.org/dc/elements/1.1/" ' \
      'xmlns:dlna="urn:schemas-dlna-org:metadata-1-0/" ' \
      'xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" ' \
      'xmlns:sec="http://www.sec.co.kr/" ' \
      'xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/">' \
      '<item restricted="1" id="PlayOn-content" parentID="">' \
      '<upnp:class>%s</upnp:class>' \
      '<dc:title>%s</dc:title>' \
      '<res protocolInfo="http-get:*:application/octet-stream:DLNA.ORG_PN=;DLNA.ORG_OP=00;DLNA.ORG_FLAGS=01700000000000000000000000000000" sec:URIType="public"%s%s>%s</res>' \
      '%s' \
      '</item>' \
      '</DIDL-Lite>' % (media_class, html.escape(title), size_arg, duration_arg, html.escape(uri), '<sec:CaptionInfoEx sec:type="%s">%s</sec:CaptionInfoEx>' %(html.escape(subtype), html.escape(suburi)) if suburi else '')
    return didl_lite
    
  def send_URI(self, renderer, uri, title, kind=None, size=None, duration=None, suburi=None, stop=None):
    didl_lite = self._build_didl(uri, title, kind, size, duration, suburi)
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'SetAVTransportURI', soap_timeout=20,  soap_stop=stop, InstanceID=0, CurrentURI=uri, CurrentURIMetaData=didl_lite)
    if not out_args:
      return None
    else:
      return True
      
  def send_Local_URI(self, renderer, uri, title, kind=None, size=None, duration=None, suburi=None, stop=None):
    didl_lite = self._build_didl(uri, title, kind, size, duration, suburi)
    didl_lite = didl_lite.replace(' sec:URIType="public"', '').replace('DLNA.ORG_OP=00', 'DLNA.ORG_OP=01').replace('DLNA.ORG_FLAGS=017', 'DLNA.ORG_FLAGS=217')
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'SetAVTransportURI', soap_timeout=20, soap_stop=stop, InstanceID=0, CurrentURI=uri, CurrentURIMetaData=didl_lite)
    if not out_args:
      return None
    else:
      return True

  def send_URI_Next(self, renderer, uri, title, kind=None, size=None, duration=None, suburi=None, stop=None):
    didl_lite = self._build_didl(uri, title, kind, size, duration, suburi)
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'SetNextAVTransportURI', soap_timeout=20,  soap_stop=stop, InstanceID=0, NextURI=uri, NextURIMetaData=didl_lite)
    if not out_args:
      return None
    else:
      return True
      
  def send_Local_URI_Next(self, renderer, uri, title, kind=None, size=None, duration=None, suburi=None, stop=None):
    didl_lite = self._build_didl(uri, title, kind, size, duration, suburi)
    didl_lite = didl_lite.replace(' sec:URIType="public"', '').replace('DLNA.ORG_OP=00', 'DLNA.ORG_OP=01').replace('DLNA.ORG_FLAGS=017', 'DLNA.ORG_FLAGS=217')
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'SetNextAVTransportURI', soap_timeout=20, soap_stop=stop, InstanceID=0, NextURI=uri, NextURIMetaData=didl_lite)
    if not out_args:
      return None
    else:
      return True

  def send_Play(self, renderer):
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'Play', InstanceID=0, Speed=1)
    if not out_args:
      return None
    else:
      return True

  def send_Stop(self, renderer):
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'Stop', InstanceID=0)
    if not out_args:
      return None
    else:
      return True
      
  def send_Pause(self, renderer):
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'Pause', InstanceID=0)
    if not out_args:
      return None
    else:
      return True

  def send_Seek(self, renderer, target="0:00:00"):
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'Seek', InstanceID=0, Unit="REL_TIME", Target=target)
    if not out_args:
      return None
    else:
      return True

  def get_Position(self, renderer):
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'GetPositionInfo', soap_timeout=3, InstanceID=0)
    if not out_args:
      return None
    return out_args['RelTime']

  def get_Duration(self, renderer):
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'GetMediaInfo', soap_timeout=3, InstanceID=0)
    if not out_args:
      return None
    return out_args['MediaDuration']

  def get_Duration_Fallback(self, renderer):
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'GetPositionInfo', soap_timeout=3, InstanceID=0)
    if not out_args:
      return None
    return out_args['TrackDuration']

  def get_TransportInfo(self, renderer):
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'GetTransportInfo', InstanceID=0)
    if not out_args:
      return None
    return out_args['CurrentTransportState'], out_args['CurrentTransportStatus']

  def get_Mute(self, renderer):
    out_args = self.send_soap_msg(renderer, 'RenderingControl', 'GetMute', InstanceID=0, Channel='Master')
    if not out_args:
      return None
    return out_args['CurrentMute']

  def set_Mute(self, renderer, mute=False):
    out_args = self.send_soap_msg(renderer, 'RenderingControl', 'SetMute', InstanceID=0, Channel='Master', DesiredMute=(1 if mute else 0))
    if not out_args:
      return None
    return True

  def get_Volume(self, renderer):
    out_args = self.send_soap_msg(renderer, 'RenderingControl', 'GetVolume', InstanceID=0, Channel='Master')
    if not out_args:
      return None
    return out_args['CurrentVolume']

  def set_Volume(self, renderer, volume=0):
    out_args = self.send_soap_msg(renderer, 'RenderingControl', 'SetVolume', InstanceID=0, Channel='Master', DesiredVolume=volume)
    if not out_args:
      return None
    return True

  def get_StoppedReason(self, renderer):
    out_args = self.send_soap_msg(renderer, 'AVTransport', 'X_GetStoppedReason', InstanceID=0)
    if not out_args:
      return None
    return out_args['StoppedReason'], out_args['StoppedReasonData']

  @staticmethod
  def _process_lastchange(value):
    try:
      lc_xml = minidom.parseString(value)
      changes = []
      for node in lc_xml.documentElement.childNodes:
        if node.nodeType == node.ELEMENT_NODE:
          break
      if node.nodeType == node.ELEMENT_NODE:
        for p_node in node.childNodes:
          if p_node.nodeType == p_node.ELEMENT_NODE:
            lc_prop_name = p_node.localName
            lc_prop_value = None
            for att in p_node.attributes.items():
              if att[0].lower() == 'val':
                lc_prop_value = att[1]
                break
            if lc_prop_value != None:
              changes.append((lc_prop_name, lc_prop_value))
      return changes
    except:
      return DLNAHandler._process_lastchange(value)

  def new_event_subscription(self, *args, **kwargs):
    EventListener = super().new_event_subscription(*args, **kwargs)
    EventListener.Renderer = EventListener.Device
    return EventListener


class HTTPExplodedMessage:

  __slots__ = ('method', 'path', 'version', 'code', 'message', 'headers', 'body', 'expect_close')

  def __init__(self):
    self.method = self.path = self.version = self.code = self.message = self.body = self.expect_close = None
    self.headers = {}

  def __bool__(self):
    return self.method is not None or self.code is not None

  def clear(self):
    self.__init__()
    return self

  def header(self, name, default=None):
    return self.headers.get(name.title(), default)

  def in_header(self, name, value):
    h = self.header(name)
    return False if h is None else (value.lower() in map(str.strip, h.lower().split(',')))

  def __repr__(self):
    if self:
      try:
        return '\r\n'.join(('<HTTPExplodedMessage at %#x>\r\n----------' % id(self), (' '.join(filter(None, (self.method, self.path, self.version, self.code, self.message)))), *map(': '.join, self.headers.items()), '----------\r\nLength of body: %s byte(s)' % len(self.body or ''), '----------\r\nClose expected: %s' % self.expect_close))
      except:
        return '<HTTPExplodedMessage at %#x>\r\n<corrupted object>' % id(self)
    else:
      return '<HTTPExplodedMessage at %#x>\r\n<no message>' % id(self)


class HTTPMessage:

  @staticmethod
  def _read_headers(msg, http_message):
    if not msg:
      return False
    a = None
    for msg_line in msg.replace('\r\n', '\n').split('\n')[:-2]:
      if a is None:
        try:
          a, b, c = msg_line.strip().split(None, 2)
        except:
          try:
            a, b, c = *msg_line.strip().split(None, 2), ''
          except:
            return False
      else:
        try:
          header_name, header_value = msg_line.split(':', 1)
        except:
          return False
        header_name = header_name.strip().title()
        if header_name:
          header_value = header_value.strip()
          if not header_name in ('Content-Length', 'Location', 'Host') and http_message.headers.get(header_name):
            if header_value:
              http_message.headers[header_name] += ', ' + header_value
          else:
            http_message.headers[header_name] = header_value
        else:
          return False
    if a is None:
      return False
    if a[:4].upper() == 'HTTP':
      http_message.version = a.upper()
      http_message.code = b
      http_message.message = c
    else:
      http_message.method = a.upper()
      http_message.path = b
      http_message.version = c.upper()
    http_message.expect_close = http_message.in_header('Connection', 'close') or (http_message.version.upper() != 'HTTP/1.1' and not http_message.in_header('Connection', 'keep-alive'))
    return True

  @staticmethod
  def _read(message, max_data, start_time, max_time, stop):
    is_stop = lambda : False if stop == None else stop.is_set()
    start_read_time = time.time()
    with selectors.DefaultSelector() as selector:
      selector.register(message, selectors.EVENT_READ)
      ready = False
      rem_time = 0.5
      while not ready and not is_stop():
        t = time.time()
        if message.timeout:
          rem_time = min(rem_time, message.timeout - t + start_read_time)
        if max_time:
          rem_time = min(rem_time, max_time - t + start_time)
        if rem_time <= 0:
          return None
        if hasattr(message, 'pending'):
          if message.pending():
            ready = True
          else:
            ready = selector.select(rem_time)
        else:
          ready = selector.select(rem_time)
        if ready:
          try:
            return message.recv(min(max_data, 1048576))
          except:
            return None
    return None

  def __new__(cls, message=None, body=True, decode='utf-8', timeout=5, max_length=1048576, max_hlength=1048576, max_time=None, stop=None):
    http_message = HTTPExplodedMessage()
    if message is None:
      return http_message
    start_time = time.time()
    max_hlength = min(max_length, max_hlength)
    rem_length = max_hlength
    iss = isinstance(message, socket.socket)
    if not iss:
      msg = message[0]
    else:
      message.settimeout(None if max_time else timeout)
      msg = b''
    while True:
      msg = msg.lstrip(b'\r\n')
      body_pos = msg.find(b'\r\n\r\n')
      if body_pos >= 0:
        body_pos += 4
        break
      body_pos = msg.find(b'\n\n')
      if body_pos >= 0:
        body_pos += 2
        break
      if not iss or rem_length <= 0:
        return http_message
      try:
        bloc = cls._read(message, rem_length, start_time, max_time, stop)
        if not bloc:
          return http_message
      except:
        return http_message
      rem_length -= len(bloc)
      msg = msg + bloc
    if not cls._read_headers(msg[:body_pos].decode('ISO-8859-1'), http_message):
      return http_message.clear()
    if not iss:
      http_message.expect_close = True
    if http_message.code in ('100', '101', '204', '304'):
      http_message.body = b''
      return http_message
    if not body:
      http_message.body = msg[body_pos:]
      return http_message
    rem_length += max_length - max_hlength
    chunked = http_message.in_header('Transfer-Encoding', 'chunked')
    if chunked:
      body_len = -1
    else:
      body_len = http_message.header('Content-Length')
      if body_len is None:
        if not iss or (http_message.code in ('200', '206') and http_message.expect_close):
          body_len = -1
        else:
          body_len = 0
      else:
        try:
          body_len = max(0, int(body_len))
        except:
          return http_message.clear()
    if http_message.in_header('Expect', '100-continue') and iss:
      if max_time:
        message.settimeout(timeout)
      try:
        if body_pos + body_len - len(msg) <= rem_length:
          message.sendall('HTTP/1.1 100 Continue\r\n\r\n'.encode('ISO-8859-1'))
        else:
          message.sendall(('HTTP/1.1 413 Payload too large\r\nContent-Length: 0\r\nDate: %s\r\nCache-Control: no-cache, no-store, must-revalidate\r\n\r\n' % email.utils.formatdate(time.time(), usegmt=True)).encode('ISO-8859-1'))
          return http_message.clear()
      except:
        return http_message.clear()
      finally:
        if max_time:
          message.settimeout(None)
    if not chunked:
      if body_len < 0:
        if not iss:
          http_message.body = msg[body_pos:]
        else:
          bbuf = BytesIO()
          rem_length -= bbuf.write(msg[body_pos:])
          while rem_length > 0:
            try:
              bw = bbuf.write(cls._read(message, rem_length, start_time, max_time, stop))
              if not bw:
                break
              rem_length -= bw
            except:
              return http_message.clear()
          if rem_length <= 0:
            return http_message.clear()
          http_message.body = bbuf.getvalue()
      elif len(msg) < body_pos + body_len:
        if not iss or body_pos + body_len - len(msg) > rem_length:
          return http_message.clear()
        bbuf = BytesIO()
        body_len -= bbuf.write(msg[body_pos:])
        while body_len:
          try:
            bw = bbuf.write(cls._read(message, body_len, start_time, max_time, stop))
            if not bw:
              return http_message.clear()
            body_len -= bw
          except:
            return http_message.clear()
        http_message.body = bbuf.getvalue()
      else:
        http_message.body = msg[body_pos:body_pos+body_len]
    else:
      bbuf = BytesIO()
      buff = msg[body_pos:]
      while True:
        chunk_pos = -1
        rem_slength = max_hlength - len(buff)
        while chunk_pos < 0:
          buff = buff.lstrip(b'\r\n')
          chunk_pos = buff.find(b'\r\n')
          if chunk_pos >= 0:
            chunk_pos += 2
            break
          chunk_pos = buff.find(b'\n')
          if chunk_pos >= 0:
            chunk_pos += 1
            break
          if not iss or rem_slength <= 0 or rem_length <= 0:
            return http_message.clear()
          try:
            bloc = cls._read(message, min(rem_length, rem_slength), start_time, max_time, stop)
            if not bloc:
              return http_message.clear()
          except:
            return http_message.clear()
          rem_length -= len(bloc)
          rem_slength -= len(bloc)
          buff = buff + bloc
        try:
          chunk_len = int(buff[:chunk_pos].split(b';', 1)[0].rstrip(b'\r\n'), 16)
          if not chunk_len:
            break
        except:
          return http_message.clear()
        if chunk_pos + chunk_len - len(buff) > rem_length:
          return http_message.clear()
        if len(buff) < chunk_pos + chunk_len:
          if not iss:
            return http_message.clear()
          chunk_len -= bbuf.write(buff[chunk_pos:])
          while chunk_len:
            try:
              bw = bbuf.write(cls._read(message, chunk_len, start_time, max_time, stop))
              if not bw:
                return http_message.clear()
              chunk_len -= bw
            except:
              return http_message.clear()
            rem_length -= bw
          buff = b''
        else:
          bbuf.write(buff[chunk_pos:chunk_pos+chunk_len])
          buff = buff[chunk_pos+chunk_len:]
      http_message.body = bbuf.getvalue()
      rem_length = min(rem_length, max_hlength - body_pos - len(buff) + chunk_pos)
      while not (b'\r\n\r\n' in buff or b'\n\n' in buff):
        if not iss or rem_length <= 0:
          return http_message.clear()
        try:
          bloc = cls._read(message, rem_length, start_time, max_time, stop)
          if not bloc:
            return http_message.clear()
        except:
          return http_message.clear()
        rem_length -= len(bloc)
        buff = buff + bloc
    if http_message.body:
      try:
        if decode:
          http_message.body = http_message.body.decode(decode)
      except:
        return http_message.clear()
    return http_message

class HTTPRequest:

  SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
  SSLContext.check_hostname = False
  SSLContext.verify_mode = ssl.CERT_NONE
  RequestPattern = \
    '%s %s HTTP/1.1\r\n' \
    'Host: %s\r\n%s' \
    '\r\n'

  def __new__(cls, url, method=None, headers=None, data=None, timeout=3, max_length=1048576, max_hlength=1048576, max_time=None, stop=None, pconnection=None, ip=''):
    if url is None:
      return HTTPMessage()
    is_stop = lambda : False if stop == None else stop.is_set()
    if method is None:
      method = 'GET' if data is None else 'POST'
    redir = 0
    try:
      url_p = urllib.parse.urlsplit(url, allow_fragments=False)
      if headers is None:
        headers = {}
      hitems = headers.items()
      if pconnection is None:
        pconnection = [None]
        hccl = True
      else:
        hccl = 'close' in (e.strip() for k, v in hitems if k.lower() == 'connection' for e in v.lower().split(','))
      headers = {k: v for k, v in hitems if not k.lower() in ('host', 'content-length', 'connection', 'expect')}
      if not 'accept-encoding' in (k.lower() for k, v in hitems):
        headers['Accept-Encoding'] = 'identity'
      if data is not None:
        if not 'chunked' in (e.strip() for k, v in hitems if k.lower() == 'transfer-encoding' for e in v.lower().split(',')):
          headers['Content-Length'] = str(len(data))
      headers['Connection'] = 'close' if hccl else 'keep-alive'
    except:
      return HTTPMessage()
    if max_time:
      start_time = time.time()
    while True:
      try:
        if max_time:
          if time.time() - start_time > max_time:
            raise
        if is_stop():
          raise
        if pconnection[0] is None:
          if url_p.scheme.lower() == 'http':
            pconnection[0] = socket.create_connection((url_p.netloc + ':80').split(':', 2)[:2], timeout=timeout, source_address=(ip, 0))
          elif url_p.scheme.lower() == 'https':
            pconnection[0] = cls.SSLContext.wrap_socket(socket.create_connection((url_p.netloc + ':443').split(':', 2)[:2], timeout=timeout, source_address=(ip, 0)), server_side=False, server_hostname=url_p.netloc.split(':')[0])
          else:
            raise
        else:
          try:
            pconnection[0].settimeout(timeout)
          except:
            pass
        if max_time:
          if time.time() - start_time > max_time:
            raise
        if is_stop():
          raise
        msg = cls.RequestPattern % (method, (url_p.path + ('?' + url_p.query if url_p.query else '')).replace(' ', '%20') or '/', url_p.netloc, ''.join(k + ': ' + v + '\r\n' for k, v in headers.items()))
        pconnection[0].sendall(msg.encode('iso-8859-1') + (data or b''))
        code = '100'
        while code == '100':
          if max_time:
            rem_time = max_time - time.time() + start_time
            if rem_time <= 0:
              raise
          if is_stop():
            raise
          resp = HTTPMessage(pconnection[0], body=(method.upper() != 'HEAD'), decode=None, timeout=timeout, max_length=max_length, max_time=(rem_time if max_time else None), stop=stop)
          code = resp.code
          if code == '100':
            redir += 1
            if redir > 5:
              raise
        if code is None:
          raise
        if code[:2] == '30' and code != '304':
          if resp.header('location'):
            url = urllib.parse.urljoin(url, resp.header('location'))
            urlo_p = url_p
            url_p = urllib.parse.urlsplit(url, allow_fragments=False)
            if headers['Connection'] == 'close' or resp.expect_close or (urlo_p.scheme != url_p.scheme or urlo_p.netloc != url_p.netloc):
              try:
                pconnection[0].close()
              except:
                pass
              pconnection[0] = None
              headers['Connection'] = 'close'
            redir += 1
            if redir > 5:
              raise
            if code == '303':
              if method.upper() != 'HEAD':
                method = 'GET'
              data = None
              for k in list(headers.keys()):
                if k.lower() in ('transfer-encoding', 'content-length', 'content-type'):
                  del headers[k]
          else:
            raise
        else:
          break
      except:
        try:
          pconnection[0].close()
        except:
          pass
        pconnection[0] = None
        return HTTPMessage()
    if headers['Connection'] == 'close' or resp.expect_close:
      try:
        pconnection[0].close()
      except:
        pass
      pconnection[0] = None
    return resp

class log_event:

  def __init__(self, kmod, verbosity):
    self.kmod = kmod
    self.verbosity = verbosity

  def log(self, level, kmsg, *var):
    if level <= self.verbosity:
      now = time.localtime()
      s_now = '%02d/%02d/%04d %02d:%02d:%02d' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec)
      try:
        print(s_now, ':', LSTRINGS[self.kmod][kmsg] % var)
      except:
        try:
          print(s_now, ':', kmsg % var)
        except:
          print(s_now, ':', kmsg)



