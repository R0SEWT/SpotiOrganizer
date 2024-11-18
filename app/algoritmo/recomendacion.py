from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from pathlib import Path


def read_csv(file_name):
    return pd.read_csv(Path(__file__).parent / "datasets/" / file_name)

def clean_data(df, cols):
    """
    Limpieza simple, sin filas con valores nulos en las columnas.
    """
    df_musica = df.dropna(subset=cols)
    return df_musica

def get_similarities(df, cols):
    """
    Obtiene la matriz de similitud de las canciones basandose en las columnas.
    """
    matriz = df[cols].to_numpy()
    matriz_similitud = cosine_similarity(matriz)
    return matriz_similitud


def get_best_recommendations(nombre_cancion, artista, matriz_similaridad, df_user):
    def get_song_index(nombre_cancion, artista, df_musica):
        """
        Obtiene el índice de la canción en el DataFrame basado en el nombre de la canción o el artista.
        """
        df_canciones = df_musica[df_musica["Track"].str.contains(nombre_cancion, regex=False)]
        
        if not df_canciones.empty:
            return df_canciones.index[0]
        else:
            return df_musica[df_musica["Artist"] == artista].index[0]
    
    def get_similar_songs_indexes(index_cancion, matriz_similaridad, temp=0.3):
        """
        Obtiene los índices de las canciones más similares, excluyendo la misma canción y las 3 más similares.
        """
        similar_song_indexes = matriz_similaridad[index_cancion].argsort()[::-1][3:10]

        # agregar canciones similares random en función de la temperatura

        return similar_song_indexes
    
    def get_ordered_songs(df_musica, similar_song_indexes, df_user, columnas_importantes):
        """
        Ordena las canciones similares según la importancia de las columnas.
        """
        mean_user = df_user[columnas_importantes].mean().to_numpy()
        idxs = mean_user.argsort()[-5:][::-1]
        orden_columnas = df_user[columnas_importantes].columns[idxs].to_list()
        canciones_ordenadas = df_musica.iloc[similar_song_indexes].sort_values(by=orden_columnas, ascending=False)
        return canciones_ordenadas[["Track", "Artist", "Uri"]].to_numpy()

    """
    Retorna el nombre de la canción que es más similar a la canción dada.
    """
    index_cancion = get_song_index(nombre_cancion, artista, df_musica)
    similar_song_indexes = get_similar_songs_indexes(index_cancion, matriz_similaridad)
    canciones_similares = get_ordered_songs(df_musica, similar_song_indexes, df_user, columnas_importantes)
    return canciones_similares


def filtro_colaborativo(df_usuarios_canciones: pd.DataFrame, id_usuario: str):
    """
    Realiza recomendaciones colaborativas basadas en la similitud de usuarios.
    """
    # Transformar el DataFrame reemplazando 0 por -1 y llenando valores nulos con 0
    df_transformed = df_usuarios_canciones.replace({0: -1}).fillna(0) 

    # Obtener el índice del usuario
    idx_user = df_usuarios_canciones[df_usuarios_canciones.id == id_usuario].index
    if idx_user.empty:
        raise ValueError(f"El usuario con id {id_usuario} no se encuentra en el DataFrame.")
    
    # Calcular la matriz de similitud de usuarios (coseno)
    matriz_similitud_usuarios = cosine_similarity(df_transformed)

    # Obtener preferencias del usuario 
    user_preferences = df_transformed.iloc[idx_user, 1:].reset_index(drop=True).loc[0]

    # Calcular la similitud de los usuarios con el usuario actual
    user_similarity = matriz_similitud_usuarios[idx_user].flatten()

    # Obtener los índices de los usuarios más similares (excluyendo el propio usuario) 

    # Top 5 usuarios similares
    similar_users_indexes = user_similarity.argsort()[::-1]
    similar_users_indexes = similar_users_indexes[similar_users_indexes != idx_user]
    similar_users_indexes = similar_users_indexes[:5]

    # Obtener las canciones preferidas por los usuarios similares
    similar_users_preferences = df_transformed.iloc[similar_users_indexes, 1:] # sin id

    # Calcular la puntuación promedio de las canciones preferidas por los usuarios similares
    mean_preferences = similar_users_preferences.mean(axis=0)

    # Ordenar las canciones por la puntuación promedio
    recommended_songs = mean_preferences.sort_values(ascending=False)

    # Filtrar las canciones que el usuario actual ya ha escuchado
    user_listened_songs = df_usuarios_canciones.iloc[idx_user, 1:].columns[user_preferences != -1]
    recommended_songs = recommended_songs.drop(user_listened_songs, errors='ignore')

    # Obtener los nombres de las canciones recomendadas
    recommended_songs_names = recommended_songs.index.tolist()

    return recommended_songs_names

def crear_df_user(data):
    df_user = pd.DataFrame(data, columns=["Track", "Artist"])
    return pd.merge(df_user, df_musica, on=["Track", "Artist"], how="inner")


df = read_csv("Spotify.csv")
columnas_importantes = ['Danceability', 'Energy', 'Speechiness', 'Acousticness', 'Instrumentalness', 'Valence', 'Tempo']
df_musica = clean_data(df, columnas_importantes)
matriz_similaridad = get_similarities(df_musica, columnas_importantes)
